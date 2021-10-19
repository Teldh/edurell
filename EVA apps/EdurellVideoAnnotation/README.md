# EDURELL Video Annotation

# Installation

Prerequisites: Anaconda


Create the virtual environment:

    conda create -n myenv python=3.6 pip pytorch
    
Activate the environment:

    conda activate myenv

Download the repository:
    
    git clone https://github.com/Mirwe/edurell_annotations.git
    
Open the repository

    cd edurell_annotations
    
Install requirements:
    
    pip install -r requirements.txt
    python -m spacy download en
    
Create a folder "punctuator" (lowercase) in the same level of the .py files, and put inside the file downloaded at the link:
https://drive.google.com/uc?id=0B7BsN5f2F1fZd1Q0aXlrUDhDbnM

Open the python console and type:

    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')
    
(Facoltative) If you have a gpu, to improve performances:

    conda install m2w64-toolchain
    conda install libpython

  
Installation completed, with the environment activated launch the project with:

    python main.py
