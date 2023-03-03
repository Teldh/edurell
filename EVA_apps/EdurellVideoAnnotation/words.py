import RAKE
from conll import lemmatize

import db_mongo
import phrasemachine
import spacy
from numpy import dot, round,empty,prod,sum,array
from numpy.linalg import norm
from sklearn.feature_extraction.text import CountVectorizer
from difflib import ndiff
import re
from typing import List
from typing_extensions import Literal
from nltk.corpus import words
from enum import Enum


class ComparisonMethod(Enum):
    TXT_SIM = 0
    TXT_LEN = 1
    MEANINGFUL_WORDS_NUM = 2
    TIME_PROXIMITY = 3
    POSITION_NOT_COLLIDING = 4


class TextSimilarityClassifier:
    '''
    Text diffences classifier
    Using various methods can check if some text is part of other text\n
    or if two texts are similar
    '''


    def __init__(self,comp_methods:List[ComparisonMethod] or None=None,txt_sim_conf:float=0.9,txt_len_conf:float=0.35,time_frames_tol = 10) -> None:
        self._CV = CountVectorizer()
        self.pattern = re.compile('[^a-zA-Z\d &-]')
        if comp_methods is None:
            self._comp_methods = {ComparisonMethod.TXT_LEN,ComparisonMethod.TXT_SIM}
        else:
            self.set_comparison_methods(comp_methods)
        self.txt_sim_conf = txt_sim_conf
        self.txt_len_conf = txt_len_conf
        self.time_frames_tol = 10
        self._words = set(words.words())

    def clean_text(self,text:str):
        return self.pattern.sub(' ',text)

    def cosine_sim_SKL(self,text1:str,text2:str,rounding_decimals:int=6):
        '''
        DEPRECATED
        ----------
        Cosine similarity computed with SKLearn, it's ~10 times slower than the FAST version
        '''
        text1_cleaned = self.clean_text(text1); text2_cleaned = self.clean_text(text2)
        texts_vectorized = self._CV.fit_transform([text1_cleaned,text2_cleaned]).toarray()
        return round(sum(prod(texts_vectorized,axis=0))/prod(norm(texts_vectorized,axis=1)),decimals=rounding_decimals)
        
    def cosine_sim_FAST(self,text1:str,text2:str,rounding_decimals:int=6) -> bool:
        '''
        DEPRECATED
        ----------
        self made cosine similarity, less precise but 10 times faster than the SKLearn version
        '''
        words_set = set()
        text1_clean_split, text2_clean_split = self.clean_text(text1).split(), self.clean_text(text2).split()
        max_len = max(len(text1_clean_split),len(text2_clean_split))
        words_set = set(text1_clean_split+text2_clean_split)
        words_dict = dict(zip(words_set,list(range(1,len(words_set)+1))))
        text1_binarized = list(map(lambda key: words_dict[key], text1_clean_split))
        text2_binarized = list(map(lambda key: words_dict[key], text2_clean_split))
        text1_binarized.extend([0]*(max_len-len(text1_binarized)))
        text2_binarized.extend([0]*(max_len-len(text2_binarized)))
        text1_binarized = array(text1_binarized)
        text2_binarized = array(text2_binarized)
        text1_norm = norm(text1_binarized)
        text2_norm = norm(text2_binarized)
        if text1_norm and text2_norm:
            return round(dot(text1_binarized,text2_binarized)/(text1_norm*text2_norm),decimals=rounding_decimals)
        else:
            return 0

    def is_partially_in(self,text1:str,text2:str,startend_frames1:'tuple[int,int] | None'=None,startend_frames2:'tuple[int,int] | None'=None,xywh1:'tuple[int,int,int,int]'=None,xywh2:'tuple[int,int,int,int]'=None) -> bool:
        '''
        Finds if text1 is partial text of text2
        texts are cleaned of all non alphanumeric characters.

        Then are compared in terms of one or more predefined methods: 
            - diffs percentage of all the merged texts with respect to a threshold\n
            - diffs percentage of the first text with respect to another threshold empirically estimated\n
            - time proximity of their frames within a tolerance\n
            - collision of their bounding boxes #TODO improve adding a tol
        
        Order is based on performance maximization
            
        ### No checks are performed on input

        -------

        Returns
        -------
        True if text1 is part of the text2

        '''
        comp_methods = self._comp_methods
        checks:list[bool] = []

        if all(checks) and ComparisonMethod.TIME_PROXIMITY in comp_methods:
            frames_tol = self.time_frames_tol
            checks.append(startend_frames2[0] - frames_tol <= startend_frames1[0] <= startend_frames1[1] <= startend_frames2[1] + frames_tol)
        
        if all(checks) and ComparisonMethod.POSITION_NOT_COLLIDING in comp_methods:
            checks.append(      xywh1[0] + xywh1[2] < xywh2[0] 
                            or  xywh2[0] + xywh2[2] < xywh1[0] 
                            or  xywh1[1] + xywh1[3] < xywh2[1] 
                            or  xywh2[1] + xywh2[3] < xywh1[1])

        if all(checks) and ComparisonMethod.TXT_SIM in comp_methods:
            text1_cleaned = self.clean_text(text1); text2_cleaned = self.clean_text(text2)
            diffs = [change[0] for change in ndiff(text1_cleaned,text2_cleaned)]
            removed_chars_count = diffs.count('-')
            checks.append(removed_chars_count/len(diffs) < 1 - self.txt_sim_conf)

        if all(checks) and ComparisonMethod.MEANINGFUL_WORDS_NUM in comp_methods:
            words = self._words
            txt1_split = text1_cleaned.split(); txt2_split = text2_cleaned.split()
            len_txt1_split = len(txt1_split); len_txt2_split = len(txt2_split) 
            checks.append(( 0 < len_txt1_split <= len_txt2_split 
                                and ( len([word for word in txt1_split if word in words]) / len(txt1_split) 
                                        <= 
                                      len([word for word in txt2_split if word in words]) / len(txt2_split)) ) 
                            or len_txt1_split <= len_txt2_split )

        if all(checks) and ComparisonMethod.TXT_LEN in comp_methods:
            checks.append(removed_chars_count/len(text1) < self.txt_len_conf)

        return all(checks)
        
    def are_cosine_similar(self,text1:str,text2:str,confidence:float=0.9) -> bool:
        '''
        Determine if two texts are cosine similar.

        This is evaluated in terms of words mapped to a unique number\n
        ### May collapse when performed on texts with num words = 1 vs 2 or 2 vs 1

        -----------

        Parameters:
        ----------
            - text1 (str): The first text to compare.
            - text2 (str): The second text to compare.
            - confidence (float, optional): The minimum confidence level required to consider
                the texts similar. Defaults to 0.9

        Returns:
        --------
            bool: True if the texts are cosine similar with a confidence level above
                `confidence`, False otherwise.  

        '''
        text1_clean_split, text2_clean_split = self.clean_text(text1).split(), self.clean_text(text2).split()
        len_split1, len_split2 = len(text1_clean_split), len(text2_clean_split)
        max_len = max(len_split1,len_split2)
        words_set = set(text1_clean_split+text2_clean_split)
        values = list(range(1,len(words_set)+1))
        words_dict = dict(zip(words_set,values))
        text1_vectorized = list(map(lambda key: words_dict[key], text1_clean_split))
        text2_vectorized = list(map(lambda key: words_dict[key], text2_clean_split))
        texts_vectorized = empty((2,max_len),dtype=int)
        texts_vectorized[0,:len_split1] = text1_vectorized; texts_vectorized[0,len_split1:] = 0
        texts_vectorized[1,:len_split2] = text2_vectorized; texts_vectorized[1,len_split2:] = 0
        return sum(prod(texts_vectorized,axis=0))/prod(norm(texts_vectorized,axis=1)) > confidence
    
    def set_comparison_methods(self,values:List[ComparisonMethod]):
        self._comp_methods = set(values)


def extract_keywords(text:str,minFrequency=1):

    text = text.replace("'ve", " have")
    text = text.replace("'re", " are")
    text = text.replace("'s", " is")
    text = text.replace("'ll", " will")

    Rake = RAKE.Rake(RAKE.SmartStopList())

    concepts = [j[0] for j in Rake.run(text, maxWords=3, minFrequency=minFrequency)[0:15]]
    nlp = spacy.load("en_core_web_sm")  # en_core_sci_scibert
    doc = nlp(text.lower())

    tokens = [token.text for token in doc]
    pos = [token.pos_ for token in doc]
    concepts_machine = phrasemachine.get_phrases(tokens=tokens, postags=pos)

    for c in concepts_machine["counts"].most_common(3):
        if len(c[0].split(" ")) < 3:
            concepts.append(c[0])

    concepts = lemmatize(concepts)

    for i, concept in enumerate(concepts):
        concepts[i] = concept.replace("-", " ").replace("/", " / ")

    #print(concepts)
    return concepts


def extract_title(text:str):
    first_sentence = text.split("\n\n")[0].lstrip().rstrip()
    if first_sentence:
        return first_sentence

def get_real_keywords(video_id, title=False, defs=True):
    graphs = db_mongo.get_graphs_info(video_id)
    if graphs is not None:
        #print("Annotator: ", graphs["annotators"][0]["name"])
        first_annotator = graphs["annotators"][0]['id']
        concept_map_annotator = db_mongo.get_concept_map(first_annotator, video_id)
        definitions = db_mongo.get_definitions(first_annotator, video_id)
        keywords = []

        if defs:
            for d in definitions:
                if d["concept"] not in keywords:
                    keywords.append(d["concept"])

        for rel in concept_map_annotator:
            if rel["prerequisite"] not in keywords:
                keywords.append(rel["prerequisite"])
            if rel["target"] not in keywords:
                keywords.append(rel["target"])

        if title:
            return graphs["title"], keywords

        return keywords
    return None

if __name__ == '__main__':
    text1 = 'Machine Learning definition\n\n* Arthur Samuel (1959). Machine Learning: Field of\nstudy that gives computers the ability to learn\nwithout being explicitly programmed.'
    text2 = 'Machine Learning definition\n\n+ Arthur Samuel (1959). Machine Learning: Field of\nstudy that gives computers the ability to learn\nwithout being explicitly programmed.\n\n* Tom Mitchell (1998) Well-posed Learning\nProblem: A computer program is said to /Jearn\nfrom experience E with respect to some task T\nand some performance measure P, if its\nperformance on T, as measured by’?, improves\nwith experience E'
    print(TextSimilarityClassifier().is_partially_in(text1,text2))