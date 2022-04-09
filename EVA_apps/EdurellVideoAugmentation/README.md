# Video augmentation and graph exploration

Prof.

- Ilaria Torre

- Ilenia Galluccio

Students.

- Thomas Neveux

- Julie Massari

<br>

### Small description of the project:

This project is a web application developped in React (JS) for the front-end and with Flask for the back-end (Python). The aim of the application is to help student learn through videos, contextual help and an interactive knowledge graph gathering all the concepts explainend in the video and the relationships with each other.

<br>

#### Link to features demo

https://drive.google.com/drive/folders/1o9WdAvNopdtUSw5h2tq0q5QBMCZbrNIk?usp=sharing

<br>

# Installation

## Virtual Environment

<br>

To organize the projecty is better to create and use a virtual env as Annotator app, but you can skip this step.

#### Prerequisites: Anaconda  

<br>

Start by running Anaconda/Conda terminal:

Create the virtual environment (if first time, or not already done for annotator app):

    > conda create -n myenv python=3.7 pip pytorch
    
Activate the environment:

    > conda activate myenv

(Facoltative) Open VSCode with conda (if dev using VScode ide)

    > code

## Back-end (Flask)

* Make sure that you have Flask installed on your machine

* Go inside flask-server folder:
  - cd src/flask-server

* Install the requirements:
  - pip install -r requirements.txt  

  (each module's version is specified in requirements.txt)

* If you need to connect to Edurell’s mail box:
  - Go to Gmail’s login interface
  - Email address : Specified in src/flask-server/main.py **(line 43)**
  - Password : Specified in src/flask-server/main.py at **(line 44)**

## Front-end (React.js)

* Make sure that Node.js and npm are installed on the machine

* Go inside react-app folder
  - cd src/react-app  

* Install the dependencies
  - npm install

# Notes

- Pymongo issues 

  if pymongo certificate is invalid:
    1. Download https://letsencrypt.org/certs/lets-encrypt-r3.pem 
    2. rename file .pem to .cer
    3. double click and install   
  
<br>

- Videos folder

  the videos folder inside main.py (line ~28) has to be arranged basing on the server folder structure.

  ```python
    app.config["CLIENT_IMAGES"] = 
    "/var/www/edurell/EVA_apps/EdurellVideoAnnotation/static/videos"
  ```
<br>

- Get synonyms from wordnet NLTK (manual annotator)

  to get synonyms automatically at the start change the commented lines on:   
  main.py - (line 265-273)

  there we have 2 ways: 
    * 1) - starting from empty
    * 2) - getting from wordnet   

  leave not commented only the choosen one.

<br>

- Synonyms on burst mode

  to select the way to proceed in the burst (auto or semiauto) you can either:
  - activate the popup to select the procedure (line 43-60 of burst_result.html file)  
    * .. by turning setPopup = true;
  - have a look and edit (burst type) on the code at:
    * burst_result (line 43-60 [popup], 300, 312)
    * burst_vocabulary (line 349-378 [launchBurstAnalysis])
    * main.py (line 494-572 [burst])   

<br>

- Email 

    After some months the email sender could stop working and you can find errors on register or forgot password:

    * Login to the google account with this app credentials   
    (you can find those credentials on file main.py line ~43) 
    
    * go to security settings -> allow less secure app

    * (More info -> https://support.google.com/accounts/answer/6010255?hl=en)

    If still not working:

    * after log in with the google account open this link:  
      https://accounts.google.com/DisplayUnlockCaptcha

    * (More info -> https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp)


<br>

# Run the application

* Open 2 terminals

  - 1st one : go to flask-server folder and run main
    - cd src/flask-server
    - python main.py  
  - 2nd one : go to react-app folder and run the start script
    - cd src/react-app
    - npm start

The app should start automatically in the default browser at this point..  
(However the url to type in the browser is the following: http://localhost:3000/)

<br>

# Deploy and run on server

Follow this guide:
https://drive.google.com/file/d/1ST-BZPppwrAWwb_fYFOcBa8HWmYOB0hG/view?usp=sharing

