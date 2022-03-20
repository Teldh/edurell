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

- Email 

    After some months the email sender could stop working and you can find errors on register or forgot password:

    * Login to the google account with this app credentials   
    (you can find those credentials on file main.py line ~43) 
    
    * go to security settings -> allow less secure app

    * (More info -> https://support.google.com/accounts/answer/6010255?hl=en)

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
https://drive.google.com/file/d/1BaBYjWEZQpeNCRy-OM74rfmW3NCP2S4u/view?usp=sharing

