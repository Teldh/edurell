import RAKE
from conll import lemmatize

import db_mongo
import phrasemachine
import spacy




def extract_keywords(text):

    text = text.replace("'ve", " have")
    text = text.replace("'re", " are")
    text = text.replace("'s", " is")
    text = text.replace("'ll", " will")

    concepts = rake_phrasemachine(text)

    for i, concept in enumerate(concepts):
        concepts[i] = concept.replace("-", " ").replace("/", " / ")

    return concepts





def rake_phrasemachine(text):
    Rake = RAKE.Rake(RAKE.SmartStopList())
    concepts = [j[0] for j in Rake.run(text, maxWords=3, minFrequency=3)[0:15]]

    nlp = spacy.load("en_core_web_sm")  # en_core_sci_scibert
    doc = nlp(text.lower())

    tokens = [token.text for token in doc]
    pos = [token.pos_ for token in doc]
    concepts_machine = phrasemachine.get_phrases(tokens=tokens, postags=pos)

    for c in concepts_machine["counts"].most_common(3):
        if len(c[0].split(" ")) < 3:
            concepts.append(c[0])

    return lemmatize(concepts)





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










