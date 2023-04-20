import RAKE
import phrasemachine
import spacy
import re

from conll import lemmatize
import db_mongo

def get_keywords_from_title(text:str):
    text = re.sub('[Dd]efinition|[Ii]ntroduction|\n',' ',text.lower())
    Rake = RAKE.Rake(RAKE.SmartStopList())
    return [keyword[0] for keyword in Rake.run(text, maxWords=3, minFrequency=1)]

def extract_keywords(text:str,maxWords=3,minFrequency=1):

    text = text.replace("'ve", " have")
    text = text.replace("'re", " are")
    text = text.replace("'s", " is")
    text = text.replace("'ll", " will")

    Rake = RAKE.Rake(RAKE.SmartStopList())

    concepts = [j[0] for j in Rake.run(text, maxWords=maxWords, minFrequency=minFrequency)[0:15]]
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

def get_real_keywords(video_id, annotator_id=None, title=False, defs=True):
    graphs = db_mongo.get_graphs_info(video_id)
    if graphs is not None:
        indx_annotator = 0
        if annotator_id is not None:
            annotators = graphs['annotators']
            for i,annot in enumerate(annotators):
                if annot['id']==annotator_id:
                    indx_annotator = i
                    break
        annotator_id = graphs["annotators"][indx_annotator]['id']
        #print("Annotator: ", graphs["annotators"][0]["name"])
        concept_map_annotator = db_mongo.get_concept_map(annotator_id, video_id)
        definitions = db_mongo.get_definitions(annotator_id, video_id)
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
    text = '=. =\n“Estimation of Stature ws\n[Avitinacint from Intact Long Limb Bones\nUniversity PGi ain «¢\n130, (Fem+Tib) +6329 +259\n238 Fem stat\nCes to.\n\na sme $337\n\n  \n  \n\n  \n    \n    \n  \n\n \n\n(Fem. Tin) +5320 +35!\n\nFi. s5o61 £357\nrib $6153 2366\n0 am\nitimemiiilimmici\nUna 45776 2430\nHum 457897\n‘rotor (970):\n{Eximation of nature from intact long ib Bonet\nInstant O(adPesonal a\nMase Blsnars 1,'
    text1 = 'Forensic Archaeology and Anthropology\nPart.4\nEstimating Stature'
    text2 = 'an\nA Ablinerrin\ni oy\n\nThis example: (2.47 x [bone measurement 45.4cm]) + 54.10cm'
    text3 = 'YY\nS [ 2blteeretiny\n\nLeaves'
    text4 = 'Machine Learning definition'
    print(get_keywords_from_title(text2))
    #print(extract_title(text))
    #print(TextSimilarityClassifier().is_partially_in(text1,text2))