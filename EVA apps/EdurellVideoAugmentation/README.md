# Video augmentation and graph exploration

### Company name

UNIGE

Professore Ilaria Torre

Ilenia Galluccio

### Students

Thomas Neveux

Julie Massari

#### Small description of the project

This project is a web application developped in React (JS) for the front-end and with Flask for the back-end (Python). The aim of the application is to help student learn through videos, contextual help and an interactive knowledge graph gathering all the concepts explainend in the video and the relationships with each other.

#### Link to features demo

https://drive.google.com/drive/folders/1o9WdAvNopdtUSw5h2tq0q5QBMCZbrNIk?usp=sharing

# Install and launch Edurell web application

## Back-end (Flask)

* Make sure that you have Flask installed on your machine
* Install the requirements:
  - pip install -r requirements.txt
  - each module's version is specified in requirements.txt
* Connect to Edurell’s mail box
  - Go to Gmail’s login interface : <https://accounts.google.com/AccountChooser/signinchooser?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&flowName=GlifWebSignIn&flowEntry=AccountChooser>
  - Email address : Specified in src/flask-server/main.py **(line 39)**
  - Password : Specified in src/flask-server/main.py at **(line 40)**
  - Account recovery address : <thomas.neveux@etu.utc.fr>

## Fron-end (React.js)

* Make sure that Node.js and npm are installed on the machine
* Install the dependencies
  - npm install

# Run the application

* Open 2 terminals
  - 1st one : go to flask-server folder and run main
    - cd src/flask-server
    - python main.py
  * 2nd one : go to react-app folder and run the start script
    - cd src/react-app
    - npm start

The url to type in the browser is the following: http://localhost:3000/


Note: if pymongo certificate is invalid:
1. Download https://letsencrypt.org/certs/lets-encrypt-r3.pem 
2. rename file .pem to .cer
3. double click and install
