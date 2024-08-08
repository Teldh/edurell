# EDURELL Video Annotation

# Installation

### Prerequisites: ffmpeg

Open a Terminal and type:
```    
sudo apt update && sudo apt upgrade
```
```
sudo apt install ffmpeg
```

### Prerequisites: Anaconda  

<br>

Start by running Anaconda/Conda terminal:

<br>

Download the repository:
```    
git clone https://github.com/Teldh/edurell.git
```

"cd" to the folder EdurellVideoAnnotation
```
cd {path to the folder EdurellVideoAnnotation}
```

conda create the python environment from a yml file
```
conda env create -f conda_environment.yml
conda activate edu_anno_env
```

Installation completed, with the environment activated launch the project with:

    > python main.py
    
<br>

# On any Change in Environment Packages 

To avoid inconsistency between local and server, yml file has been used to enforce same environment state

open a terminal
```
cd {inside folder EKEELVideoAnnotation}
```

replace the conda_environment.yml inside using
```
conda env export --no-builds | grep -v "^prefix: " | grep -v "en-core-web-sm" > conda_environment.yml
```

to synchronize the changes in the server push updates to the repo and on the server terminal

```
cd {inside folder EKEELVideoAnnotation}
conda env update --file conda_environment.yml --prune
```

# Notes:
    
- Save burst auto and semiauto on DB

    To save into db the burst results decomment the lines of code (544-569) of main.py

- Get synonyms from wordnet NLTK (manual annotator)

  to get synonyms automatically at the start change the commented lines on:   
  main.py - (line 265-273)

  there we have 2 ways: 
    * 1) - starting from empty
    * 2) - getting from wordnet   

  leave not commented only the choosen one.

- Synonyms on burst mode

  to select the way to proceed in the burst (auto or semiauto) you can either:
  - activate the popup to select the procedure (line 43-60 of burst_result.html file)  
    * .. by turning setPopup = true;
  - have a look and edit (burst type) on the code at:
    * burst_result (line 43-60 [popup], 300, 312)
    * burst_vocabulary (line 349-378 [launchBurstAnalysis])
    * main.py (line 494-572 [burst])   

- Variables:   

    If you change the name of the virtual-environment 
    then you have to change the path in the first rows of segmentation.py:
    
    ```python
    incompatible_path = '/home/anaconda3/envs/{ENV NAME}/bin'
    ```
- Email 

    After some months the email sender could stop working and you can find errors on register or forgot password:

    * Login to the google account with this app credentials   
    (you can find those credentials on file sendmail.py line ~126) 
    
    * go to security settings -> allow less secure app

    * (More info -> https://support.google.com/accounts/answer/6010255?hl=en)

    If still not working:

    * after log in with the google account open this link:  
      https://accounts.google.com/DisplayUnlockCaptcha

    * (More info -> https://stackoverflow.com/questions/16512592/login-credentials-not-working-with-gmail-smtp)

# Run locally

Start by running Anaconda/Conda terminal:

<br>

Activate the "myenv" virtual environment:

    > conda activate edu_anno_env

(Facoltative) Open VSCode with conda (if dev using VScode ide)

    > code

With the environment activated launch the app locally with:

    > python main.py

# Deploy and run on server

Follow this guide:
https://raw.githubusercontent.com/Teldh/edurell/201093006ae2117c5aabea1fd356fe08218dfcd0/docs/server_guide.pdf