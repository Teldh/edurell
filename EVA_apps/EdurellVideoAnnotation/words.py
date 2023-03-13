from conll import lemmatize
import db_mongo

import RAKE
import phrasemachine
import spacy

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


def extract_title(text:str):
    """
    Need rework
    """
    assert False, "not implemented"
    if '\n\n' in text:
        first_sentence = text.split('\n\n')[0].lstrip().rstrip()
        return first_sentence if not '\n' in first_sentence else None
    has_keywords = False
    i = 0
    text_split = text.split('\n')
    len_text_split = len(text_split)
    while not has_keywords and i < len_text_split:
        has_keywords = bool(extract_keywords(text_split[i]))
    if i == len_text_split: return None
    else:
        return text_split[i]

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
    text = '=. =\n“Estimation of Stature ws\n[Avitinacint from Intact Long Limb Bones\nUniversity PGi ain «¢\n130, (Fem+Tib) +6329 +259\n238 Fem stat\nCes to.\n\na sme $337\n\n  \n  \n\n  \n    \n    \n  \n\n \n\n(Fem. Tin) +5320 +35!\n\nFi. s5o61 £357\nrib $6153 2366\n0 am\nitimemiiilimmici\nUna 45776 2430\nHum 457897\n‘rotor (970):\n{Eximation of nature from intact long ib Bonet\nInstant O(adPesonal a\nMase Blsnars 1,'
    text1 = 'Forensic Archaeology and Anthropology\nPart.4\nEstimating Stature'
    text2 = 'an\nA Ablinerrin\ni oy\n\nThis example: (2.47 x [bone measurement 45.4cm]) + 54.10cm'
    text3 = 'YY\nS [ 2blteeretiny\n\nLeaves'
    print(extract_title(text))
    #print(TextSimilarityClassifier().is_partially_in(text1,text2))