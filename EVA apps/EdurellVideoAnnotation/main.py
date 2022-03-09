import copy

import rdflib
from config import app
import db_mongo
from db_mongo import users, unverified_users
from flask import render_template, jsonify, request, session, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
import video
import segmentation
from ontology import create_graph_jsonld
from werkzeug.urls import url_parse
from forms import addVideoForm, RegisterForm, LoginForm, GoldStandardForm, ForgotForm, PasswordResetForm, ConfirmCodeForm, BurstForm
from keywords import extract_keywords, get_real_keywords
from conll import conll_gen, lemmatize,create_text
from nltk import WordNetLemmatizer
from audio_transcription import speech_from_youtube
import bcrypt
from analysis import data_summary, compute_agreement, linguistic_analysis, fleiss
from user import User
from sendmail import send_mail, generate_confirmation_token, confirm_token, send_confirmation_mail
from create_gold_standard import create_gold
import random
import string
import json
from conll import get_text
from burst_class import burst_extraction
from metrics import calculate_metrics
from synonyms import create_skos_dictionary, get_synonyms_from_list
from skos_synonyms_query import try_query

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
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('user/login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
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
    form = addVideoForm()
    videos = db_mongo.get_videos()

    if form.validate_on_submit():

        try:
            url = form.url.data
            vid_id, title, creator, video_duration = video.download(url)

            subtitles, autogenerated = speech_from_youtube(url)

            # segment the video with semantic similarity
            start_times, end_times, images_path, text = segmentation.segmentation(url, 0.22, 35, 1, 15, subtitles, vid_id)

            lemmatized_concepts = db_mongo.get_extracted_keywords(vid_id)
            if lemmatized_concepts is None:
                print("Extracting main concepts..")
                concepts = extract_keywords(text)

                print("Lemmatizing concepts..")
                lemmatized_concepts = lemmatize(concepts)




            db_mongo.insert_video({"video_id":vid_id, "title":title, "creator":creator, "segment_starts":start_times,
                                   "segment_ends": end_times, "extracted_keywords": lemmatized_concepts})


            print("Creating and uploading conll..")
            conll_sentences = conll_gen(vid_id,text)
            print(len(conll_sentences))
            print("Creating text..")
            lemmatized_subtitles, all_lemmas = create_text(subtitles, autogenerated, conll_sentences)

            annotator = current_user.complete_name

            relations = db_mongo.get_concept_map(current_user.mongodb_id, vid_id)
            definitions = db_mongo.get_definitions(current_user.mongodb_id, vid_id)

            # Obtaining concept vocabulary from DB
            #conceptVocabulary  = db_mongo.get_vocabulary(current_user.mongodb_id, vid_id)
            conceptVocabulary = None

            # If the concept vocabulary is new (empty) in DB then initialize it to empty synonyms
            if(conceptVocabulary == None) :
                conceptVocabulary = {}
                for i in lemmatized_concepts :
                    conceptVocabulary[i] = [];

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
            print(e)
            flash(e, "danger")

    return render_template('video_selection.html', form=form, videos=videos)


'''
Get concept vocabulary (dict: word -> synonyms)
'''
@app.route('/get_concept_vocabulary', methods=["GET", "POST"])
def get_concept_vocabulary():
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
    lemmatizer = WordNetLemmatizer()

    splitted_word = word.split(" ")
    lemma = ""

    for i, w in enumerate(splitted_word):
        lemma += lemmatizer.lemmatize(w)
        if i < len(splitted_word)-1:
            lemma += " "

    print(lemma)
    return jsonify({'lemma': lemma.lower()})


@app.route('/json_ld', methods=["GET", "POST"])
def jsonld():
    #if request.method == 'POST':
    annotations = request.json
    #print(annotations)
    g, json = create_graph_jsonld(annotations)

    data = json.copy()
    data["video_id"] = annotations["id"]
    data["annotator_id"] = current_user.mongodb_id
    data["annotator_name"] = current_user.complete_name
    data["email"] = current_user.email
    data["conceptVocabulary"] = create_skos_dictionary(annotations["conceptVocabulary"])

    # inserting annotations on DB
    db_mongo.insert_graph(data)

    result = {
        "graph": json,
        "conceptVocabulary": data["conceptVocabulary"]
    }

    return result


@app.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    video_choices = db_mongo.get_graphs_info()

    if request.method == 'POST':
        analysis_type = request.form["analysis_type"]

        if analysis_type == "data_summary":
            video_id = request.form["video"]
            annotator_id = request.form["annotator"]

            concept_map = db_mongo.get_concept_map(annotator_id, video_id)
            definitions = db_mongo.get_definitions(annotator_id, video_id)

            results = data_summary(concept_map, definitions, video_id)

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
    #form = addVideoForm()
    form = BurstForm()
    videos = db_mongo.get_videos()

    if form.validate_on_submit():

        video_id = form.url.data

        text = get_text(video_id)
        conll_sentences = conll_gen(video_id, text)

        k = get_real_keywords(video_id, title=True)
        if k is None:
            # keywords = rake_phrasemachine(text)
            title, keywords = db_mongo.get_extracted_keywords(video_id, title=True)
        else:
            title = k[0]
            keywords = k[1]


        # semi-automatic extraction
        if form.type.data == "semi":

            subtitles, autogenerated = speech_from_youtube("https://www.youtube.com/watch?v="+video_id)

            lemmatized_subtitles, all_lemmas = create_text(subtitles, autogenerated, conll_sentences)

            return render_template('burst_results.html', result=subtitles, video_id=video_id, concepts=keywords,
                                   title=title, lemmatized_subtitles=lemmatized_subtitles, all_lemmas=all_lemmas,
                                   type="semi")

        elif form.type.data == "auto":
            return render_template('burst_results.html', result=[], video_id=video_id, concepts=keywords, title=title,
                                   lemmatized_subtitles=[], all_lemmas=[], type="auto")

    return render_template('burst.html', form=form, videos=videos)



@app.route('/burst_launch', methods=["GET", "POST"])
def burst_launch():
    data = request.json
    video_id = data["id"]
    concepts = data["concepts"]

    #print(concepts)

    concept_map, definitions = burst_extraction(video_id, concepts)
    results = data_summary(concept_map, definitions, video_id)

    json = {
        "concepts": concepts,
        "concept_map": concept_map,
        "definitions": definitions,
        "data_summary": results,
        "agreement": None,
    }

    graphs = db_mongo.get_graphs_info(video_id)
    if graphs is not None:
        #print(graphs["annotators"][0])
        first_annotator = graphs["annotators"][0]['id']
        concept_map_annotator = db_mongo.get_concept_map(first_annotator, video_id)

        veo, pageRank, LO, PN, ged_sim = calculate_metrics(concept_map, concept_map_annotator, concepts)

        json["agreement"] = {
            "name":graphs["annotators"][0]["name"],
            "K": compute_agreement(concept_map, concept_map_annotator)["agreement"],
            "VEO": veo,
            "GED": ged_sim,
            "pageRank": round(pageRank, 3),
            "LO": round(LO, 3),
            "PN": round(PN, 3)
        }


    return json


# from color_histogram import get_image_from_video
# @app.route('/test_image', methods = ['GET', 'POST'])
# def test_image():
#
#     encoded_img_data = get_image_from_video('sXLhYStO0m8', "auricular_surface", 166, 5,16,29,65)
#     return render_template('test_image.html', img_data=encoded_img_data.decode('utf-8'))
#

if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=True, debug=False) #, port=5050\
    
    