from flask import Flask, abort, request, jsonify, g, url_for, send_from_directory
from os import sep
from youtube_transcript_api import YouTubeTranscriptApi
import time
import random
import string
import math

from datetime import datetime
from flask_httpauth import HTTPBasicAuth
import jwt
import bcrypt
from flask_mongoengine import MongoEngine
from flask_mail import Mail, Message
from smtplib import SMTPException, SMTPRecipientsRefused
import urllib.request
import json
import urllib

import data
import handle_data


app = Flask(__name__)
app.config['SECRET_KEY'] = 'random_key'

#segment images directory
app.config["CLIENT_IMAGES"] = "../../../edurell/edurell/static/videos"


#mongo db config
user = "luca"
password = "vSmAZ6c1ZOg2IEVw"
app.config['MONGODB_SETTINGS'] = {
    'db': 'edurell',
    'host': "mongodb+srv://"+user+":"+password+"@clusteredurell.z8aeh.mongodb.net/edurell?retryWrites=true&w=majority"
}

#mail server config (gmail account date of birth : 01/01/1900)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'project.edurell@gmail.com'
app.config['MAIL_PASSWORD'] = 'work$package'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'project.edurell@gmail.com'

# extensions
auth = HTTPBasicAuth(scheme='Custom')
db = MongoEngine()
db.init_app(app)
mail = Mail(app)

# generate a random string of lenght N composed of lowercase letters and numbers
def generate_code(N=6):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(N))


# Get the speech from a youtube video URL
@app.route('/api/youtube_transcript', methods=["GET", "POST"])
def speech_from_youtube():
    req = request.get_json(force=True)
    videoId=req.get('video_id')
    x = YouTubeTranscriptApi.get_transcript(videoId, languages=['en'])
    subs_dict = []
    for sub in x:
        start = get_integer_part(sub["start"])
        duration = get_integer_part(sub["duration"])
        subs_dict.append(
            {"text": sub["text"],
             "start": start,
             "end": start + duration}
        )
    result = jsonify(subs_dict)
    return result

# get the integer part of a number
# ex: for 2.5 it will return 2
def get_integer_part(number):
    split_number = math.modf(number)
    return split_number[1]

#image of the mongodb collection of the database, used by mongoengine
class Videos(db.Document):
    video_id = db.StringField()
    title = db.StringField()
    creator = db.StringField()
    segment_starts = db.ListField(db.StringField())
    segment_ends = db.ListField(db.StringField())
    extracted_keywords = db.ListField(db.StringField())

#image of the mongodb collection of the database, used by mongoengine
class VideoStatistics(db.Document):
    video_url = db.StringField()
    amountViewers = db.IntField()
    total_fragment_clicks = db.IntField()
    total_node_clicks = db.IntField()
    total_transcript_clicks = db.IntField()
    total_searchbar_clicks = db.IntField()
    viewersList = db.ListField(db.StringField())

#image of the mongodb collection of the database, used by mongoengine
class HisloryLog(db.EmbeddedDocument):
    date = db.DateTimeField()
    request = db.StringField()

#image of the mongodb collection of the database, used by mongoengine
class Fragment(db.EmbeddedDocument):
    name = db.StringField()
    start = db.StringField()
    end =  db.StringField()
    progress = db.IntField()

#image of the mongodb collection of the database, used by mongoengine
class VideoHistory(db.EmbeddedDocument):
    video_url = db.StringField()
    video_watchtime = db.IntField()
    fragment_clicks = db.IntField()
    node_clicks = db.IntField()
    transcript_clicks = db.IntField()
    searchbar_clicks = db.IntField()
    notes = db.StringField()
    lastChangesDate = db.DateTimeField()
    fragments_progress = db.EmbeddedDocumentListField(Fragment)
    logs = db.EmbeddedDocumentListField(HisloryLog)


# image of the mongodb collection of the database, used by mongoengine
# also have some methods related to the fields of the class
class Student(db.Document):
    name = db.StringField()
    surname = db.StringField()
    email = db.StringField()
    password_hash = db.StringField()

    code_reset_password = db.StringField()
    nb_try_code_reset_password = db.IntField()

    code_delete_account = db.StringField()
    nb_try_code_delete_account = db.IntField()

    video_history_list = db.EmbeddedDocumentListField(VideoHistory)

    def hash_password(self, password):
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = hashed_pwd.decode('utf8')
        self.save()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))



    def hash_code_reset_password(self, code):
        hashed_code = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt())
        self.code_reset_password = hashed_code.decode('utf8')
        self.save()

    def verify_code_reset_password(self, code):
        nb_try_code_reset_password_to_increment = self.nb_try_code_reset_password
        if nb_try_code_reset_password_to_increment is None:
            nb_try_code_reset_password_to_increment=0
        self.nb_try_code_reset_password = nb_try_code_reset_password_to_increment+ 1
        self.save()
        return bcrypt.checkpw(code.encode('utf-8'), self.code_reset_password.encode('utf-8'))



    def hash_code_delete_account(self, code):
        hashed_code = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt())
        self.code_delete_account = hashed_code.decode('utf8')
        self.save()

    def verify_code_delete_account(self, code):
        nb_try_code_delete_account_to_increment = self.nb_try_code_delete_account
        if nb_try_code_delete_account_to_increment is None:
            nb_try_code_delete_account_to_increment=0
        self.nb_try_code_delete_account = nb_try_code_delete_account_to_increment + 1
        self.save()
        return bcrypt.checkpw(code.encode('utf-8'), self.code_delete_account.encode('utf-8'))



    def generate_auth_token(self, expires_in=600):
        #return jwt.encode(
        #    {'email': self.email, 'exp': time.time() + expires_in},
        #    app.config['SECRET_KEY'], algorithm='HS256')
        return jwt.encode(
            {'email': self.email},
            app.config['SECRET_KEY'], algorithm='HS256')


    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return Student.objects(email=data['email']).first()

#image of the mongodb collection of the database, used by mongoengine
# this is used to store the accounts that are not verified yet with the confirmation code sent by mail
class UnverifiedStudent(db.Document):
    name = db.StringField()
    surname = db.StringField()
    email = db.StringField()
    password_hash = db.StringField()

    code_on_creation_hash = db.StringField()
    nb_try_code_on_creation = db.IntField()


    def hash_password(self, password):
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = hashed_pwd.decode('utf8')
        self.save()

    def hash_code_on_creation(self, code):
        hashed_code = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt())
        self.code_on_creation_hash = hashed_code.decode('utf8')
        self.save()

    def verify_code_on_creation(self, code):
        nb_try_code_on_creation_to_increment = self.nb_try_code_on_creation
        if nb_try_code_on_creation_to_increment is None:
            nb_try_code_on_creation_to_increment=0
        self.nb_try_code_on_creation = nb_try_code_on_creation_to_increment+ 1
        self.save()
        return bcrypt.checkpw(code.encode('utf-8'), self.code_on_creation_hash.encode('utf-8'))

#function used by the authentication system. If it returns true, the user is considered as logged in, false he's not
@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    student = Student.verify_auth_token(email_or_token)
    if not student:
        # try to authenticate with email/password
        student = Student.objects(email=email_or_token).first()
        if not student or not student.verify_password(password):
            return False
    g.student = student
    return True

# api to call to create a new account
@app.route('/api/register', methods=['POST'])
def new_student():
    email_input = request.json.get('email')
    password_input = request.json.get('password')
    name_input = request.json.get('name')
    surname_input = request.json.get('surname')
    if email_input is None or password_input is None or name_input is None or surname_input is None:
        abort(400)    # missing arguments
    if Student.objects(email=email_input).first() is not None:
        abort(409, "An account have already been created with this mail")    # existing student
    existingUnverifiedStudent = UnverifiedStudent.objects(email=email_input).first()
    if existingUnverifiedStudent is not None:
        existingUnverifiedStudent.delete()

    generated_code_creation = generate_code()
    # create an UnverifiedStudent and save it in the db
    unverifiedStudent = UnverifiedStudent(email=email_input, name= name_input, surname = surname_input,nb_try_code_on_creation = 0)
    unverifiedStudent.hash_password(password_input)
    unverifiedStudent.hash_code_on_creation(generated_code_creation)
    unverifiedStudent.save()

    #send a mail with the verification code
    msg = Message('Edurell- Code to finalize your account creation', recipients = [email_input])
    msg.body = "Hello, welcome to Edurell ! \n Your validation code to finalize your account creation : "+ generated_code_creation
    try:
        mail.send(msg)
    except SMTPRecipientsRefused:
        abort(406,"invalid mail")
    except :
        abort(503, "error returned by the email sending service")
    return (jsonify({'email': unverifiedStudent.email}), 201)

# api to call to finalize your account creation (verify that your code is correct)
@app.route('/api/register/verify', methods=['POST'])
def verify_mail():
    email_input = request.json.get('email')
    code_input = request.json.get('code')
    if email_input is None or code_input is None:
        abort(400, "The code or the email is missing")    # missing arguments
    if Student.objects(email=email_input).first() is not None:
        abort(409,"An account have already been created with this mail")    # existing student
    unverifiedStudent = UnverifiedStudent.objects(email=email_input).first()
    if unverifiedStudent is None:
        abort(404, "No temporary student found, please restart register from the beginning")    # not existing UnverifiedStudent
    if not unverifiedStudent.verify_code_on_creation(code_input):
        if unverifiedStudent.nb_try_code_on_creation is not None and unverifiedStudent.nb_try_code_on_creation>5:
            unverifiedStudent.delete()
            abort(403, "Too many wrong validation code, please restart register from the beginning")
        abort(401, "Wrong validation code")

    #after the checks have passed, create a Student in the db and delete the UnverifiedStudent from the db
    student = Student(email = unverifiedStudent.email, name = unverifiedStudent.name, surname = unverifiedStudent.surname, password_hash = unverifiedStudent.password_hash)
    student.save()
    unverifiedStudent.delete()
    return (jsonify({'email': student.email}), 201)


# api to call to retrieve your password, it will send you a code by mail that you will need to return with your new password to the next api to finalize the operation
@app.route('/api/retrieve_password', methods=['POST'])
def send_code_to_reset_password_by_mail():
    email_input = request.json.get('email')
    if email_input is None:
        abort(400)    # missing arguments
    student = Student.objects(email=email_input).first()
    if student is None:
        abort(409, "No account associated with this mail")    # no existing student
    generated_code_reset_password = generate_code()
    student.hash_code_reset_password(generated_code_reset_password)
    student.save()

    #send a mail with the verification code
    msg = Message('Edurell- Code to change your password', recipients = [email_input])
    msg.body = "Hello ! \n Here is your validation code to change your password : "+ generated_code_reset_password
    mail.send(msg)
    return (jsonify({'email': student.email}), 201)

# api to call to reset your password, you need to have the right code to validate the operation
@app.route('/api/retrieve_password/verify', methods=['POST'])
def verify_code_and_change_password():
    email_input = request.json.get('email')
    code_input = request.json.get('code')
    new_password_input = request.json.get('password')
    if email_input is None or code_input is None:
        abort(400, "The code or the email is missing")    # missing arguments
    student = Student.objects(email=email_input).first()
    if student is None:
        abort(409, "No account exists with this mail")    # no existing student
    if not student.verify_code_reset_password(code_input):
        if student.nb_try_code_reset_password is not None and student.nb_try_code_reset_password>5:
            student.code_reset_password = None
            student.nb_try_code_reset_password = None
            student.save()
            abort(403, "Too many wrong validation codes, please restart the password retrieval procedure")
        abort(401, "Wrong validation code")

    else:
        student.hash_password(new_password_input)
        student.code_reset_password = None
        student.nb_try_code_reset_password = None
        student.save()
        return (jsonify({'email': student.email}), 201)


# api to call to change your name and surname, no code required
@app.route('/api/change_name_and_surname', methods=['POST'])
@auth.login_required
#the above line require that the credentials (mail/password or token) are sent in the request to login th user
def change_name_and_surname():
    name_input = request.json.get('name')
    surname_input = request.json.get('surname')
    if name_input is None or surname_input is None:
        abort(400, "The new name or/and the new surname is/are missing")    # missing arguments
    student= g.student
    student.name = name_input
    student.surname = surname_input
    student.save()
    return (jsonify({'email': student.email, 'newName': name_input, 'newSurname': surname_input}), 201)


# api to call to delete your account, it will send you a code by mail that you will need to return to the next api to finalize the operation
@app.route('/api/delete_account', methods=['POST'])
@auth.login_required
def send_code_to_delete_account_by_mail():
    email_input = request.json.get('email')
    if email_input is None:
        abort(400)    # missing arguments
    student = Student.objects(email=email_input).first()
    if student is None:
        abort(409, "No account associated with this mail")    # no existing student
    generated_code_delete_account = generate_code()
    student.hash_code_delete_account(generated_code_delete_account)
    student.save()

    #send a mail with the verification code
    msg = Message('Edurell- Code to delete your account', recipients = [email_input])
    msg.body = "Hello ! \n Here is your validation code to delete your account : "+ generated_code_delete_account+"\n Be carefull, account deletion can't be undone"
    mail.send(msg)
    return (jsonify({'email': student.email}), 201)

# api to call to delete your account, you need to have the right code to validate the operation
@app.route('/api/delete_account/verify', methods=['POST'])
@auth.login_required
def verify_code_and_delete_account():
    email_input = request.json.get('email')
    code_input = request.json.get('code')
    if email_input is None or code_input is None:
        abort(400, "The code or the email is missing")    # missing arguments
    student = Student.objects(email=email_input).first()
    if student is None:
        abort(409, "No account exists with this mail")    # no existing student
    if not student.verify_code_delete_account(code_input):
        if student.nb_try_code_delete_account is not None and student.nb_try_code_delete_account>5:
            student.code_delete_account = None
            student.nb_try_code_delete_account = None
            student.save()
            abort(403, "Too many wrong validation codes, please restart the account deletion procedure")
        abort(415, "Wrong validation code")

    else:
        data.delete_graphs(email_input)
        student.delete()
        return (jsonify({'email': student.email}), 201)


# return the name and surname of the student
@app.route('/api/get_user_infos')
@auth.login_required
def get_student():
    return jsonify({'name': g.student.name, 'surname':g.student.surname, 'email': g.student.email})

#return an authentication token, valid for a certain amount of time
@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.student.generate_auth_token()
    return jsonify({'token': token, 'duration': None, 'name': g.student.name, 'surname':g.student.surname})


#update the user history for one specific video
@app.route('/api/update_user_history',  methods=['POST'])
@auth.login_required
def add_history():
    student= g.student
    #get data from request
    video_url_input = request.json.get('url')
    video_watchtime_input = request.json.get('video_watchtime')
    fragment_clicks_input = request.json.get('fragment_clicks')
    node_clicks_input = request.json.get('node_clicks')
    transcript_clicks_input = request.json.get('transcript_clicks')
    searchbar_clicks_input = request.json.get('searchbar_clicks')
    notes_input = request.json.get('notes')
    fragments_input = request.json.get('fragments')

    if video_url_input is None:
        abort(400, "The video url is missing")    # missing arguments

    #set None numbers to zero to avoid errors in the sums
    if fragment_clicks_input is None:
        fragment_clicks_input=0
    if node_clicks_input is None:
        node_clicks_input=0
    if transcript_clicks_input is None:
        transcript_clicks_input=0
    if searchbar_clicks_input is None:
        searchbar_clicks_input=0


    videoHistory=None
    try :
        #case where the student already watched the video and the history exsists for this video
        videoHistory = student.video_history_list.get(video_url=video_url_input)

        if video_watchtime_input is not None:
            videoHistory.video_watchtime= video_watchtime_input

        if notes_input is not None:
            videoHistory.notes= notes_input

        if fragments_input is not None:
            if videoHistory.fragments_progress is not None:
                videoHistory.fragments_progress.delete()
            for item in fragments_input:
                new_fragment = Fragment(name = item['name'], start= item['start'], end= item['end'], progress=item['progress'])
                videoHistory.fragments_progress.append(new_fragment)


        videoHistory.fragment_clicks = videoHistory.fragment_clicks + fragment_clicks_input
        videoHistory.node_clicks = videoHistory.node_clicks + node_clicks_input
        videoHistory.transcript_clicks = videoHistory.transcript_clicks + transcript_clicks_input
        videoHistory.searchbar_clicks = videoHistory.searchbar_clicks + searchbar_clicks_input
        videoHistory.lastChangesDate = datetime.now()

        new_log = HisloryLog(date = datetime.now(), request = str(request.json) )
        videoHistory.logs.append(new_log)

    except:

        #case where the student have not already watched the video, we need to create a VideoHistory object for this video

        if video_watchtime_input is None:
            video_watchtime_input=0

        if notes_input is None:
            notes_input=''



        videoHistory = VideoHistory(video_url = video_url_input, video_watchtime = video_watchtime_input, fragment_clicks = fragment_clicks_input, node_clicks = node_clicks_input, transcript_clicks = transcript_clicks_input,  searchbar_clicks = searchbar_clicks_input, notes = notes_input, lastChangesDate = datetime.now())

        new_log = HisloryLog(date = datetime.now(), request = str(request.json) )
        videoHistory.logs.append(new_log)

        if fragments_input is not None:
            for item in fragments_input:
                new_fragment = Fragment(name = item['name'], start= item['start'], end= item['end'], progress=item['progress'])
                videoHistory.fragments_progress.append(new_fragment)

        student.video_history_list.append(videoHistory)

    student.save()

    #store global video statistics
    videoStatistics = VideoStatistics.objects(video_url = video_url_input).first()

    if videoStatistics is None :
        videoStatistics = VideoStatistics(video_url = video_url_input, total_fragment_clicks = fragment_clicks_input, total_node_clicks = node_clicks_input, total_transcript_clicks = transcript_clicks_input,  total_searchbar_clicks = searchbar_clicks_input, amountViewers = 1)
        videoStatistics.viewersList.append(student.email)

    else:
        videoStatistics.total_fragment_clicks = videoStatistics.total_fragment_clicks + fragment_clicks_input
        videoStatistics.total_node_clicks = videoStatistics.total_node_clicks + node_clicks_input
        videoStatistics.total_transcript_clicks = videoStatistics.total_transcript_clicks + transcript_clicks_input
        videoStatistics.total_searchbar_clicks = videoStatistics.total_searchbar_clicks + searchbar_clicks_input

        if videoStatistics.viewersList.count(student.email)==0 :
            videoStatistics.viewersList.append(student.email)
            videoStatistics.amountViewers = videoStatistics.amountViewers + 1


    videoStatistics.save()
    return (jsonify({'email': student.email}), 201)

# return the history of a user
@app.route('/api/get_user_history')
@auth.login_required
def get_history():
    student= g.student
    video_title_list = []
    for i in student.video_history_list:
        video_title_list.append(get_video_title_from_url(i.video_url.split("watch?v=")[1]))
    return (jsonify({'email': student.email, 'videoHistory' : student.video_history_list, 'videoHistoryTitles': video_title_list}), 201)


# used in the function above to get youtube video title based on their id
def get_video_title_from_url(video_id):
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % video_id}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())

    return data['title']

# return the fragment of a video and their progress, can be taken from the Video mongodb collection or from the user's history if he already watched it
@app.route('/api/get_fragments/<string:video_id>')
@auth.login_required
def get_fragments(video_id):
    student= g.student
    video_url = "https://www.youtube.com/watch?v=%s" % video_id
    video_fragment_progress = None
    for i in student.video_history_list:
        if video_url == i.video_url:
            '''print(i.fragments_progress)
            for e in i.fragments_progress:
                print(e.name)'''

            video_fragment_progress = i.fragments_progress
    graph_object = Graphs.objects(video_id = video_id, email = student.email).first()
    
    #if user first time on this video open first available video
    if(graph_object is None):
        graph_object = Graphs.objects(video_id = video_id).first()

    #if then graph still not exist show msg
    if graph_object is None:
        abort(409, "Unexisting graph for this video id")    # the video doesn't exist in the graphs collection

    keywords = handle_data.get_definitions_fragments(graph_object.email, video_id, video_fragment_progress)
    #print(keywords)


    if(video_fragment_progress is None or not len(video_fragment_progress)):
        video = Videos.objects(video_id = video_id, email = student.email).first()
        
        #if user first time on this video open first available video
        if(video is None):
            video = Videos.objects(video_id = video_id).first()
        
        #if then video still not exist show msg
        if video is None:
            abort(409, "video not in the catalog")    # the video is not in the catalog

        segment_amount = len(video.segment_starts)
        video_fragment_progress = []
        
        '''if video_id =="sXLhYStO0m8":
            names = ["Sex determination Pelvis Sciatic notch", "Pre-auricular sulcus Ventral arc Iliopubic ramus","Skull","Eye sockets", "Forehead Mastoid process Posterior zygomatich arch", "Nuchal crest", "Femur"]
            for i in range(segment_amount):
                video_fragment_progress.append({'name': names[i], 'start' : time.strftime('%H:%M:%S', time.gmtime(int(round(video.segment_starts[i])))),  'end' : time.strftime('%H:%M:%S', time.gmtime(int(round(video.segment_ends[i])))), 'progress':0 })

        else:'''

        for i in range(segment_amount):
            video_fragment_progress.append({'name': 'Part %s'%(i+1), 'start' : time.strftime('%H:%M:%S', time.gmtime(int(round(video.segment_starts[i])))),  'end' : time.strftime('%H:%M:%S', time.gmtime(int(round(video.segment_ends[i])))), 'progress':0 })

        

    return (jsonify({'email': student.email, 'fragments' : video_fragment_progress, 'keywords':keywords}), 201)

# return the list of every video available on the db
@app.route('/api/get_catalog')
@auth.login_required
def get_catalog():

    graphs = Graphs.objects()
    videos = Videos.objects()

    catalog = []
    
    for v in videos:
        for gr in graphs:
            if v.video_id == gr.video_id:
                if v not in catalog:
                    catalog.append(v)


    return (jsonify({'catalog': catalog}), 201)

#image of the mongodb collection of the database, used by mongoengine
class Graphs(db.Document):
    video_id = db.StringField()
    annotator_name = db.StringField()
    annotator_id = db.StringField()
    email = db.StringField()
    graph = db.DynamicField()
    conceptVocabulary = db.DynamicField()


#get the complete json graph from a video (put the video_id in the route)
@app.route('/api/get_graph/<string:video_id>')
@auth.login_required
def get_graph(video_id=None):
    if video_id is None:
        abort(400, "The video id is missing")    # missing arguments
    student= g.student
    graph_object = Graphs.objects(video_id = video_id, email=student.email).first()

    #if user first time on this video open first available video
    if(graph_object is None):
        graph_object = Graphs.objects(video_id = video_id).first()

    #if then graph still not exist show msg
    if graph_object is None:
        abort(409, "Unexisting graph for this video id")    # the video doesn't exist in the graphs collection

    if graph_object.conceptVocabulary is None:
        graph_object.conceptVocabulary = False

    return (jsonify({'email': student.email, 'graph' : graph_object.graph, 'conceptVocabulary': graph_object.conceptVocabulary}), 201)


# return the image of a fragment, the image is stored on the local files of the server
@app.route("/api/get_image/<string:video_id>/<int:fragment_index>")
def get_image(video_id=None, fragment_index=None ):

    if video_id is None or fragment_index is None:
        abort(400, "The video id or the image name is missing")    # missing arguments

    #get the starting time of the segment to know the image file name
    video = Videos.objects(video_id = video_id).first()
    if video is None:
        abort(409, "video not in the catalog")    # the video doesn't exist

    #segment_starting_time = None
    #try :
    #    segment_starting_time = video.segment_starts[fragment_index]
    #except IndexError:
    #    abort(409, "fragment index out of range ")

    #image_name = str(segment_starting_time).replace('.','_')+'.jpg'
    image_name = str(fragment_index).replace('.','_')+'.jpg'
    try:
        return send_from_directory(app.config["CLIENT_IMAGES"]+sep+video_id, filename= image_name, as_attachment=True)
    except FileNotFoundError:
        abort

#return the graph user ids of a given video
@app.route('/api/graph_id/<video_id>')
@auth.login_required
def graph_id(video_id):
    student= g.student
    graph_list = handle_data.check_graphs(video_id,student.email)

    # if user first time on this video, select all available graph ids
    if not len(graph_list):
        graph_list = handle_data.get_graphs(video_id)

    return {"graphs_id_list": graph_list }

#return the graph of a given video
@app.route('/api/graph/<annotator_id>/<video_id>')
@auth.login_required
def graph(annotator_id, video_id):
    concept_graph = data.build_array(annotator_id, video_id)
    
    # old: return {"conceptsList": concept_graph }
    
    conceptVocabulary = data.get_concept_vocabulary(annotator_id, video_id)

    # If the concept vocabulary is new (empty) in DB then initialize it to empty synonyms
    if(conceptVocabulary == None) :
        conceptVocabulary = {}
        concept_list = data.get_concept_list(annotator_id, video_id)
        for c in concept_list:
            conceptVocabulary[c["name"][4:].replace("_", " ")] = []

    return {"conceptsList": concept_graph, "conceptVocabulary": conceptVocabulary}

if __name__ == '__main__':
    app.run(debug=True)



# authentication system made with this tutorial : https://blog.miguelgrinberg.com/post/restful-authentication-with-flask