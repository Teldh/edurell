from flask import render_template, jsonify, request, session, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
#from werkzeug.urls import url_parse
from urllib.parse import urlparse
from nltk import WordNetLemmatizer
import bcrypt
import random
import string
import json
from conll import get_text
from burst_class import burst_extraction, burst_extraction_with_synonyms, convert_to_skos_concepts
from metrics import calculate_metrics
from multiprocessing import Manager
from audio_transcription import speech_from_youtube
from config import app
import db_mongo
from db_mongo import users, unverified_users
from video import download
from segmentation import VideoAnalyzer, workers_queue_scheduler
from ontology import annotations_to_jsonLD
from burst_class import create_local_vocabulary, create_burst_graph
from forms import addVideoForm, RegisterForm, LoginForm, GoldStandardForm, ForgotForm, PasswordResetForm, ConfirmCodeForm, BurstForm
from words import extract_keywords, get_real_keywords
from conll import conll_gen, create_text
from analysis import compute_data_summary, compute_agreement, linguistic_analysis, fleiss
from user import User
from sendmail import send_mail, generate_confirmation_token, confirm_token, send_confirmation_mail
from create_gold_standard import create_gold
from synonyms import create_skos_dictionary, get_synonyms_from_list

video_segmentations_queue = Manager().list()
workers_queue_scheduler(video_segmentations_queue)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        next_page = url_for('index')
        return redirect(next_page)

    if form.validate_on_submit():
        user = User(form.email.data)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('user/login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    print("***** EDURELL - Video Annotation: db_mongo.py::register() ******")

    form = RegisterForm()
    if form.validate_on_submit():
        password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        password_hash = password.decode('utf8')

        # generate a random string of lenght N composed of lowercase letters and numbers

        code = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        hashed_code = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt())
        code_on_creation_hash = hashed_code.decode('utf8')

        new_user = {
            'name': form.name.data,
            'surname': form.surname.data,
            'email': form.email.data,
            'password_hash': password_hash,
            'code_on_creation_hash': code_on_creation_hash,
            'nb_try_code_on_creation': 0
        }

        unverified_users.insert_one(new_user)

        send_confirmation_mail(form.email.data, code)


        mail = json.dumps(form.email.data)
        next_page = url_for('confirm_code', mail=mail)
        return redirect(next_page)

    return render_template('user/register.html', form=form)


@app.route('/confirm_code', methods=['POST', 'GET'])
def confirm_code():
    print("***** EDURELL - Video Annotation: db_mongo.py::confirm_code() ******")

    form = ConfirmCodeForm()
    email = json.loads(request.args['mail'])
    
    if form.validate_on_submit():

        code = form.code.data

        user = unverified_users.find_one({"email": email})

        if bcrypt.checkpw(code.encode('utf-8'), user["code_on_creation_hash"].encode('utf-8')):

            new_user = {
                'name': user["name"],
                'surname': user["surname"],
                'email': user["email"],
                'password_hash': user["password_hash"],
                'video_history_list': []
            }
            # users.insert_one(new_user)
            unverified_users.delete_one({"email": email})
            users.insert_one(new_user)

            flash('Thanks! Email confirmed, you can now log in', 'success')

        else:
            tries = user["nb_try_code_on_creation"] + 1
            new = {"$set": {"nb_try_code_on_creation": tries}}
            unverified_users.update_one({"email": email}, new)


    return render_template('user/confirm_code.html', form=form)


'''
Mail con link usata nel caso un utente si registri ma non attiva subito l'account, 
quindi non è più in grado di raggiungere il link
'''


@app.route('/confirm/<token>')
def confirm_email(token):
    print("***** EDURELL - Video Annotation: db_mongo.py::confirm_email() ******")

    try:
        print(token)
        email = confirm_token(token)

        u = unverified_users.find_one({"email": email})
        new_user = {
            'name': u["name"],
            'surname': u["surname"],
            'email': u["email"],
            'password_hash': u["password_hash"],
            'video_history_list': []
        }
        # users.insert_one(new_user)
        unverified_users.delete_one({"email": email})
        users.insert_one(new_user)

        us = User(email)
        login_user(us)

        flash('Thanks! Email confirmed', 'success')
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    return render_template('index.html')



@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    print("***** EDURELL - Video Annotation: db_mongo.py::forgot_password() ******")

    form = ForgotForm()

    if form.validate_on_submit():
        token = generate_confirmation_token(form.email.data)
        reset_url = url_for('password_reset', token=token, _external=True)
        html = render_template('user/user_forgot_password_mail.html', reset_url=reset_url)
        subject = "Password reset"

        send_mail(form.email.data, subject, html)
        flash('Email sent to ' + form.email.data, 'success')



    return render_template('user/forgot_password.html', form=form)



@app.route('/password_reset/<token>', methods=['POST', 'GET'])
def password_reset(token):
    print("***** EDURELL - Video Annotation: db_mongo.py::password_reset() ******")

    form = PasswordResetForm()

    try:
        email = confirm_token(token)

        if form.validate_on_submit():
            hashpass = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            password_hash = hashpass.decode('utf8')
            db_mongo.reset_password(email, password_hash)
            flash('Password updated', 'success')

        return render_template('user/password_reset.html', form=form)

    except:
        flash('The link is invalid or has expired.', 'danger')
        return render_template('index.html')




@app.route('/video_selection', methods=['GET', 'POST'])
@login_required
def video_selection():
    print("***** EDURELL - Video Annotation: main.py::video_selection(): Inizio ******")
    form = addVideoForm()
    videos = db_mongo.get_videos()

    if form.validate_on_submit():
        try:
            url = form.url.data
            vid_id, title, creator, video_duration = download(url)
            vid_analyzer = VideoAnalyzer(vid_id)
            subtitles, autogenerated = vid_analyzer.get_transcript()

            # find segmentation in server
            segmentation_data = db_mongo.get_video_segmentation(vid_id,raise_error=False)
            if segmentation_data is None:
                if vid_analyzer.can_be_analyzed():
                    print("Video not already segmented: starting segmentation...")
                    global video_segmentations_queue
                    video_segmentations_queue.append(vid_id)
                else: print("The video is too long to be analyzed")
                # create thumbnails based on the previous segmentation
                start_times,end_times,images_path,text = vid_analyzer.transcript_segmentation(subtitles)
            else:
                vid_analyzer.set(segmentation_data['video_slidishness'],slidish_frames_startend=segmentation_data['slidish_frames_startend'])
                if vid_analyzer.is_slide_video():
                    assert segmentation_data["slide_startends"], "video has been segmented but has been classified as non slidish enough, remove the segmentation info from the db and reload"
                    vid_analyzer.set(slide_startends=segmentation_data["slide_startends"])
                    # create thumbnails based on slide segmentation
                    print('Creating thumbnails...')
                    start_times,end_times,images_path = vid_analyzer.create_thumbnails()
                    print(start_times)
                    _, _, text = vid_analyzer.transcript_segmentation(subtitles,create_thumbnails=False)
                else:
                    # create thumbnails based on the previous segmentation
                    start_times,end_times,images_path,text = vid_analyzer.transcript_segmentation(subtitles)

            lemmatized_concepts = db_mongo.get_extracted_keywords(vid_id)
            if lemmatized_concepts is None:
                print("Extracting and lemmatizing main concepts..")
                lemmatized_concepts = extract_keywords(text,minFrequency=3)
            # Comment to prevent uploading to database
            db_mongo.insert_video_data({"video_id":vid_id, "title":title, "creator":creator,"duration":video_duration, "segment_starts":start_times,
                                   "segment_ends": end_times, "extracted_keywords": lemmatized_concepts})

            conll_sentences = conll_gen(vid_id,text)
            lemmatized_subtitles, all_lemmas = create_text(subtitles, autogenerated, conll_sentences)

            annotator = current_user.complete_name

            relations = db_mongo.get_concept_map(current_user.mongodb_id, vid_id)
            definitions = db_mongo.get_definitions(current_user.mongodb_id, vid_id)

            # Obtaining concept vocabulary from DB
            conceptVocabulary  = db_mongo.get_vocabulary(current_user.mongodb_id, vid_id)
            
            # If the concept vocabulary is in the DB then initialize concept to the ones of the vocabulary
            if(conceptVocabulary != None) :
                lemmatized_concepts = []
                for key in conceptVocabulary:
                    lemmatized_concepts.append(key)

            # If the concept vocabulary is new (empty) in DB then initialize it
            if(conceptVocabulary == None) :

                #-----------------------------------------------------------------
                # 1) Automatically obtain synonyms using wordnet NLTK
                #
                #conceptVocabulary = get_synonyms_from_list(lemmatized_concepts)

                # 2) Start with empty synonyms in concept vocabulary
                #
                conceptVocabulary = {}
                for i in lemmatized_concepts :
                    conceptVocabulary[i] = []
                #-----------------------------------------------------------------

            for rel in relations:
                if rel["prerequisite"] not in lemmatized_concepts:
                    lemmatized_concepts.append(rel["prerequisite"])

                if rel["target"] not in lemmatized_concepts:
                    lemmatized_concepts.append(rel["target"])

            return render_template('mooc_annotator.html', result=subtitles, vid_id=vid_id, start_times=start_times,
                                   images_path=images_path, concepts=lemmatized_concepts,video_duration=video_duration, 
                                   lemmatized_subtitles=lemmatized_subtitles, annotator=annotator, conceptVocabulary=conceptVocabulary,
                                   title=title, all_lemmas=all_lemmas, relations=relations, definitions=definitions)
        except Exception as e:
            print("Exception: ")
            print(e)
            flash(e, "danger")

    print("***** EDURELL - Video Annotation: main.py::video_selection(): Fine ******")

    return render_template('video_selection.html', form=form, videos=videos)


'''
Get concept vocabulary (dict: word -> synonyms)
'''
@app.route('/get_concept_vocabulary', methods=["GET", "POST"])
def get_concept_vocabulary():
    print("***** EDURELL - Video Annotation: db_mongo.py::get_concept_vocabulary() ******")

    data = request.json

    # Getting concepts:
    concepts = data["concepts"]
    # Finding synonyms with NLTK Wordnet:
    conceptVocabulary = get_synonyms_from_list(concepts)

    json = {
        #"concepts": concepts,
        "conceptVocabulary": conceptVocabulary
    }

    return json


@app.route('/lemmatize_word/<path:word>')
def lemmatize_word(word):
    print("***** EDURELL - Video Annotation: db_mongo.py::lemmatize_word() ******")

    lemmatizer = WordNetLemmatizer()

    splitted_word = word.split(" ")
    lemma = ""

    for i, w in enumerate(splitted_word):
        lemma += lemmatizer.lemmatize(w)
        if i < len(splitted_word)-1:
            lemma += " "

    #print(lemma)
    return jsonify({'lemma': lemma.lower()})


@app.route('/upload_graph', methods=["GET", "POST"])
def upload_annotated_graph():

    print("***** EDURELL - Video Annotation: main.py::upload_annotations(): Inizio ******")
    annotations = request.json

    _, json = annotations_to_jsonLD(annotations,isAutomatic=False)

    data = json.copy()
    data["video_id"] = annotations["id"]
    data["annotator_id"] = current_user.mongodb_id
    data["annotator_name"] = current_user.complete_name
    data["email"] = current_user.email
    data["conceptVocabulary"] = create_skos_dictionary(annotations["conceptVocabulary"], annotations["id"],"manu")

    data["graph"]["@graph"].extend([{"id": x["id"], "type" : "skos:Concept"} for x in data["conceptVocabulary"]["@graph"]])


    # inserting annotations on DB
    try: 
        db_mongo.insert_graph(data)    
    except Exception as e:
        print(e)
        flash(e,"error")
        return {"done":False}

    print("***** EDURELL - Video Annotation: main.py::upload_annotations(): Fine ******")
    # TODO show a message on screen
    return {"done":True}


# download graph on the manual annotator side
@app.route('/download_graph', methods=["GET", "POST"])
def prepare_annotated_graph():
    print("***** EDURELL - Video Annotation: main.py::download_graph(): Inizio ******")

    annotations = request.json

    _, json = annotations_to_jsonLD(annotations,isAutomatic=False)

    conceptVocabulary = create_skos_dictionary(annotations["conceptVocabulary"], annotations["id"],"manu")
    
    json["graph"]["@graph"].append({ "id":"localVocabulary","type": "skos:Collection","skos:member": [elem for elem in conceptVocabulary["@graph"]]})

    result = {
        "@context": conceptVocabulary["@context"],
        "@graph": json["graph"]["@graph"]
    }

    print("***** EDURELL - Video Annotation: main.py::download_annotated_graph(): Fine ******")
    # real download happens on the js side
    return result   


@app.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    print("***** EDURELL - Video Annotation: db_mongo.py::analysis() ******")

    video_choices = db_mongo.get_graphs_info()

    if request.method == 'POST':
        analysis_type = request.form["analysis_type"]

        if analysis_type == "data_summary":
            video_id = request.form["video"]
            annotator_id = request.form["annotator"]

            concept_map = db_mongo.get_concept_map(annotator_id, video_id)
            definitions = db_mongo.get_definitions(annotator_id, video_id)

            results = compute_data_summary(video_id,concept_map, definitions)

            if annotator_id != "Burst":
                user = db_mongo.get_user(annotator_id)
                annotator = user["name"] + " " + user["surname"]

            else:
                annotator = "Burst"

            return render_template('analysis_results.html', results=results, annotator=annotator, title=video_choices[video_id]["title"])

        elif analysis_type == "agreement":
            video_id = request.form["video"]
            annotator1_id = request.form["annotator1"]
            annotator2_id = request.form["annotator2"]

            concept_map1 = db_mongo.get_concept_map(annotator1_id, video_id)
            concept_map2 = db_mongo.get_concept_map(annotator2_id, video_id)

            results = compute_agreement(concept_map1, concept_map2)

            if annotator1_id != "Burst":
                u1 = db_mongo.get_user(annotator1_id)
                results["annotator1"] = u1["name"] + " " + u1["surname"]
            else:
                results["annotator1"] = "Burst"

            if annotator2_id != "Burst":
                u2 = db_mongo.get_user(annotator2_id)
                results["annotator2"] = u2["name"] + " " + u2["surname"]
            else:
                results["annotator2"] = "Burst"


            return render_template('analysis_results.html', results=results, title=video_choices[video_id]["title"])

        elif analysis_type == "linguistic":
            video_id = request.form["video"]
            annotator_id = request.form["annotator"]

            results = linguistic_analysis(annotator_id, video_id)

            return render_template('analysis_results.html', results=results, title=video_choices[video_id]["title"])


        elif analysis_type == "fleiss":
            video_id = request.form["video"]

            results = fleiss(video_id)

            return render_template('analysis_results.html', results=results, analysis_type=analysis_type,
                                   title=video_choices[video_id]["title"])


    return render_template('analysis_selection.html',  video_choices=video_choices) #form=form,


@app.route('/gold_standard', methods=['GET', 'POST'])
@login_required
def gold_standard():
    print("***** EDURELL - Video Annotation: db_mongo.py::gold_standard() ******")

    form = GoldStandardForm()

    video_choices = db_mongo.get_graphs_info()
    form.video.choices = [(c, video_choices[c]["title"]) for c in video_choices]

    # WTFORM impone che tutte le scelte siano definite prima, quindi metto tutti gli annotatori possibili,
    # verranno poi filtrati cliccando il video

    for v in video_choices:
        for annotator in video_choices[v]["annotators"]:
            choice = (annotator["id"], annotator["name"])
            if choice not in form.annotators.choices:
                form.annotators.choices.append(choice)

    if form.validate_on_submit():
        create_gold(form.video.data, form.annotators.data, form.agreements.data, form.name.data)

    return render_template('gold_standard.html',  video_choices=video_choices, form=form)



@app.route('/burst', methods=['GET', 'POST'])
@login_required
def burst():
    print("***** EDURELL - Video Annotation: db_mongo.py::burst() ******")

    #form = addVideoForm()
    form = BurstForm()
    videos = db_mongo.get_videos()

    if form.validate_on_submit():

        video_id = form.url.data

        text = get_text(video_id)
        conll_sentences = conll_gen(video_id, text)
        # [NOTE] this has been changed to extract my keywords, not those found by the first annotator
        k = get_real_keywords(video_id,annotator_id = current_user.mongodb_id,title=True)
        if k is None :#or form.type.data == "video":  # ENABLE or part to use conceptVocabulary obtained automatically without any manual annotation on video extraction
            # keywords = rake_phrasemachine(text)
            title, keywords = db_mongo.get_extracted_keywords(video_id, title=True)
        else:
            title = k[0]
            keywords = k[1]
        
        # semi-automatic extraction
        if form.type.data == "semi":

            subtitles, autogenerated = speech_from_youtube(video_id)

            lemmatized_subtitles, all_lemmas = create_text(subtitles, autogenerated, conll_sentences)

            return render_template('burst_results.html', result=subtitles, video_id=video_id, concepts=keywords,
                                   title=title, lemmatized_subtitles=lemmatized_subtitles, all_lemmas=all_lemmas,
                                   type="semi")

        return render_template('burst_results.html', result=[], video_id=video_id, concepts=keywords, title=title,
                                lemmatized_subtitles=[], all_lemmas=[], type=form.type.data)

    return render_template('burst.html', form=form, videos=videos)



@app.route('/burst_launch', methods=["GET", "POST"])
def burst_launch():
    print("***** EDURELL - Video Annotation: main.py::burst_launch() ******")
    data = request.json

    video_id = data["id"]
    concepts = data["concepts"]
    concept_vocabulary = data["conceptVocabulary"]
    syn_burst = data["syn_burst"]
    burst_type = data["burst_type"]    
    
    # select burst type
    if syn_burst:
        print("Starting Burst " + burst_type + " with synonyms")
        concept_map,definitions = burst_extraction_with_synonyms(video_id, concepts, concept_vocabulary)
    else:
        print("Starting Burst " + burst_type)
        concept_map,definitions = burst_extraction(video_id,concepts)
    if burst_type == "semi":
        user = current_user.complete_name.replace(" ","_")+"_Burst_Analysis"
        name = current_user.complete_name
        email = current_user.email
    else:
        user = "Burst_Analysis"
        name = user
        email = user
    burst_graph = db_mongo.get_graph(user,video_id)

    # saving burst_graph on db if not already present
    if burst_graph is None:
        print("Saving Burst Graph on DB...")
        _,burst_graph = create_burst_graph(video_id,definitions,concept_map)
        local_vocabulary = create_local_vocabulary(video_id,concept_vocabulary)
        skos_concepts = local_vocabulary["skos:member"]
        downloadable_jsonld_graph = {"@context":burst_graph["@context"],"@graph":burst_graph["@graph"].copy()+[local_vocabulary]}
        burst_graph["@graph"].extend([{"id":concept["id"],"type":concept["type"]} for concept in skos_concepts])
        db_mongo.insert_graph({ "video_id":video_id,
                                "annotator_id":user,
                                "annotator_name":name,
                                "email":email,
                                "graph": burst_graph,
                                "conceptVocabulary": {"@context": burst_graph["@context"], 
                                                      "@graph": skos_concepts}})
    else:
        graph = sorted(burst_graph["@graph"],key=lambda x: int(x["id"][3:]) if str(x["id"][3:]).isnumeric() else 1042)
        for i,node in reversed(list(enumerate(graph))):
            if not str(node["id"]).startswith("concept_"):
                break
            else:
                graph.pop(i)
        downloadable_jsonld_graph = {"@context":burst_graph["@context"],"@graph":graph+[create_local_vocabulary(video_id,concept_vocabulary)]}

    data_summary = compute_data_summary(video_id,concept_map,definitions)
    
    # checks whether video has been segmented and if so if it is classifies ad slide video or not in order to enable refinement
    segmentation_data = db_mongo.get_video_segmentation(video_id,raise_error=False)
    can_be_refined = segmentation_data is not None \
                    and VideoAnalyzer(video_id).set(segmentation_data['video_slidishness']).is_slide_video()
    
    can_be_refined = can_be_refined and "slide_titles" in segmentation_data.keys()
    
    json = {
        "concepts": concepts,
        "concept_map": concept_map,
        "definitions": definitions,
        "data_summary": data_summary,
        "downloadable_jsonld_graph": downloadable_jsonld_graph,
        "agreement": None,
        "can_be_refined": can_be_refined
    }

    graphs = db_mongo.get_graphs_info(video_id)
    if graphs is not None:
        #first_annotator = graphs["annotators"][0]['id']
        #concept_map_annotator = db_mongo.get_concept_map(first_annotator, video_id)

        annotators = graphs["annotators"]
        # [NOTE] used me as annotator instead of annotators[0] for testing keywords
        my_id = current_user.mongodb_id
        indx_annotator = 0
        for i,annot in enumerate(annotators):
            if annot['id']==my_id:
                indx_annotator = i
                break
        indx_annotator = 0
        annotator = graphs["annotators"][indx_annotator]['id']
        concept_map_annotator = db_mongo.get_concept_map(annotator, video_id)

        veo, pageRank, LO, PN, ged_sim = calculate_metrics(concept_map, concept_map_annotator, concepts)

        json["agreement"] = {
            "name":graphs["annotators"][indx_annotator]["name"].replace("_"," "),
            "K": compute_agreement(concept_map, concept_map_annotator)["agreement"],
            "VEO": veo,
            "GED": ged_sim,
            "pageRank": round(pageRank, 3),
            "LO": round(LO, 3),
            "PN": round(PN, 3)
        }
    
    return json

@app.route('/refinement', methods=["GET", "POST"])
def video_segmentation_refinement():
    data = request.json
    video_id = data["id"]
    concept_vocabulary = data["conceptVocabulary"]

    # for design this should not return None
    segmentation_data = db_mongo.get_video_segmentation(video_id,returned_fields={"video_slidishness","slide_startends","slide_titles"},raise_error=False)
    new_concepts,definitions = VideoAnalyzer(video_id) \
                                .set(segmentation_data['video_slidishness'],segmentation_data['slide_startends'],titles=segmentation_data['slide_titles']) \
                                .adjust_or_insert_definitions_and_indepth_times(data["definitions"],_show_output=True)
    #from pprint import pprint
    #pprint(definitions)
    _,burst_graph = create_burst_graph(video_id,definitions,data["concept_map"])
    local_vocabulary = create_local_vocabulary(video_id,concept_vocabulary)
    skos_concepts = local_vocabulary["skos:member"]
    if len(new_concepts) > 0:
        skos_concepts.extend(convert_to_skos_concepts(new_concepts,concept_vocabulary))
    downloadable_jsonld_graph = {"@context":burst_graph["@context"],"@graph":burst_graph["@graph"].copy()+[local_vocabulary]}
    burst_graph["@graph"].extend([{"id":concept["id"],"type":concept["type"]} for concept in skos_concepts])

    db_mongo.insert_graph({ "video_id":video_id,
                            "annotator_id":current_user.complete_name.replace(" ","_")+"_Burst_Analysis",
                            "annotator_name":"Burst_Analysis",
                            "email":"Burst_Analysis",
                            "graph": burst_graph,
                            "conceptVocabulary": {"@context": burst_graph["@context"], "@graph": skos_concepts}})

    return {"definitions":definitions,
            "downloadable_jsonld_graph":downloadable_jsonld_graph}

# from color_histogram import get_image_from_video
# @app.route('/test_image', methods = ['GET', 'POST'])
# def test_image():
#
#     encoded_img_data = get_image_from_video('sXLhYStO0m8', "auricular_surface", 166, 5,16,29,65)
#     return render_template('test_image.html', img_data=encoded_img_data.decode('utf-8'))
# https://www.youtube.com/watch?v=PPLop4L2eGk
DEBUG = False

def open_application_in_browser(address):
    from webbrowser import open as open_page
    open_page('http://'+address+':5000/', new=2)

#workers_queue_scheduler(video_segmentations_queue)

if __name__ == '__main__':
    print("***** EDURELL - Video Annotation: main.py::__main__ ******")

    address = '127.0.0.1'
    #open_application_in_browser(address)    
    app.run(host=address, threaded=True, debug=DEBUG) #, port=5050\