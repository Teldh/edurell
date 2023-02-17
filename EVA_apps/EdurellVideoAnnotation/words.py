import RAKE
from conll import lemmatize

import db_mongo
import phrasemachine
import spacy
from numpy import dot, round, array
from numpy.linalg import norm
from sklearn.feature_extraction.text import CountVectorizer

class TextSimilarityClassifier:

    def __init__(self) -> None:
        self._CV = CountVectorizer()

    def cosine_sim_SKL(self,text1:str,text2:str,rounding_decimals:int=6):
        '''
        Cosine similarity computed with SKLearn, it's ~10 times slower than the FAST version
        '''
        texts_vectorized = self._CV.fit_transform([text1,text2]).toarray()
        text1_vectorized = texts_vectorized[0,:]
        text2_vectorized = texts_vectorized[1,:]
        return round(dot(text1_vectorized,text2_vectorized.T)/(norm(text1_vectorized)*norm(text2_vectorized)),decimals=rounding_decimals)
        
    def cosine_sim_FAST(self,text1:str,text2:str,rounding_decimals:int=6):
        '''
        self made cosine similarity, less precise but 10 times faster than the SKLearn version
        '''
        words_set = set()
        text1_split, text2_split = text1.split(), text2.split()
        max_len = max(len(text1_split),len(text2_split))
        words_set = set(text1_split+text2_split)
        words_dict = dict(zip(words_set,list(range(1,len(words_set)+1))))
        text1_binarized = list(map(lambda key: words_dict[key], text1_split))
        text2_binarized = list(map(lambda key: words_dict[key], text2_split))
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

from difflib import ndiff
import re

def is_partially_in(text1,text2,confidence=0.99):
    pattern = re.compile('[\W_]+')
    len_text1 = len(text1)
    text1_stripped = pattern.sub('', text1[:len_text1])
    text2_stripped = pattern.sub('', text2[:len_text1])
    diff = ndiff(text1_stripped, text2_stripped)
    tot = sum([change[0] != " " for change in diff])
    return 1 - tot/len_text1 >= confidence

def extract_keywords(text,minFrequency=1):

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
    print(is_partially_in(text1,text2))