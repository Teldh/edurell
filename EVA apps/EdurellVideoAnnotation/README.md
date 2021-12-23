# EDURELL Video Annotation

# Installation

Prerequisites: Anaconda


Create the virtual environment:

    conda create -n myenv python=3.6 pip pytorch
    
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
    
    
    
    
    
    
    
 Note:
 YouTube just removed the dislike count, for this reason the pafy package it returns an error. 
 Until there is a patch use:
 pip uninstall -y pafy
 pip install git+https://github.com/Cupcakus/pafy
