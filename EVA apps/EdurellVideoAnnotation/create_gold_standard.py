import db_mongo
from ontology import create_graph_jsonld
from pprint import pprint


def create_gold(video, annotators, combination_criteria, name):

    relations = []
    definitions = []
    if combination_criteria == "union":
        for annotator in annotators:
            relations += db_mongo.get_concept_map(annotator, video)
            definitions += db_mongo.get_definitions(annotator, video)

        annotations = {"relations":relations, "definitions":definitions, "id":video}
        g, jsonld = create_graph_jsonld(annotations, isGoldCreation=True)

        data = jsonld.copy()
        data["video_id"] = video
        data["graph_type"] = "gold standard"
        data["gold_name"] = name

        db_mongo.insert_gold(data)


    print(relations)



