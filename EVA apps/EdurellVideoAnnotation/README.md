# EDURELL Video Annotation

# Installation

Prerequisites: Anaconda


Create the virtual environment:

    conda create -n myenv python=3.7 pip pytorch
    
Activate the environment:

    conda activate myenv

Download the repository:
    
    git clone https://github.com/Teldh/edurell.git
    
"cd" to the folder EdurellVideoAnnotation
    
Install requirements:
    
    pip install -r requirements.txt
    python -m spacy download en
    
Create a folder "punctuator" (lowercase) in the same level of the .py files, and put inside the file downloaded at the link:
https://drive.google.com/drive/folders/1NYyehpB5fAlL42_TwTnXLokLz8K-TS3W?usp=sharing

Open the python console and type:

    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    
(Facoltative) If you have a gpu, to improve performances:

    conda install m2w64-toolchain
    conda install libpython

  
Installation completed, with the environment activated launch the project with:

    python main.py
    

    
- Note 1:  

    YouTube just removed the dislike count, for this reason the pafy package returns an error. 
    Until there is a patch use:

        pip uninstall -y pafy
        pip install git+https://github.com/Cupcakus/pafy

- Note 2:  

    Updated python version to 3.7.11
    Packeges must be adapted to that version

- Note 3:   

    If you change the name of the virtual-environment 
    then you have to change the path in the first rows of segmentation.py:
    
    ```python
    incompatible_path = '/home/anaconda3/envs/{ENV NAME}/bin'
    ```