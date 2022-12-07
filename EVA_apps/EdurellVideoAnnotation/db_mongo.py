import pymongo
import time
from pprint import pprint
from rdflib import Graph, plugin
import json
import pyld
from bson.json_util import dumps
from bson.son import SON
from bson import ObjectId

#pip install pymongo
#pip3 install pymongo[srv]

# client = pymongo.MongoClient(
#         'mongodb+srv://Luca:edurellMongo@cluster0.ktoan.mongodb.net/edurell?retryWrites=true&w=majority')

user = "luca"
password = "vSmAZ6c1ZOg2IEVw"

client = pymongo.MongoClient(
    "mongodb+srv://"+user+":"+password+"@clusteredurell.z8aeh.mongodb.net/edurell?retryWrites=true&w=majority")

db = client.edurell

users = db.student
unverified_users = db.unverified_student

def string_to_seconds(str):

    s = str.split("^^")[0].split(":")
    seconds = int(s[2]) + int(s[1]) * 60 + int(s[0]) * 60 * 60

    return seconds


# def mail_confirmed(email):
#     collection = db.users
#     query = {"email": email}
#
#     if collection.find_one(query) is not None:
#         new = {"$set": {"email_confirmed": True}}
#         collection.update_one(query, new)

def reset_password(email, password):
    query = {"email": email}

    if users.find_one(query) is not None:
        new = {"$set": {"password_hash": password}}
        users.update_one(query, new)

def insert_graph(data):
    collection = db.graphs
    query = {
        "annotator_id": data["annotator_id"],
        "annotator_name": data["annotator_name"],
        "email": data["email"],
        "video_id": data["video_id"]
    }

    if collection.find_one(query) is None:
        collection.insert_one(data)
    else:
        new_graph = {"$set": {"graph": data["graph"], "conceptVocabulary": data["conceptVocabulary"]}}
        collection.update_one(query, new_graph)


def insert_burst(data):
    collection = db.graphs
    query = {
        "extraction_method": "Burst",
        "video_id": data["video_id"]
    }

    if collection.find_one(query) is None:
        collection.insert_one(data)
    else:
        new_graph = {"$set": {"graph": data["graph"]}}
        collection.update_one(query, new_graph)

def insert_gold(data):
    collection = db.graphs
    query = {
        "graph_type": "gold_standard",
        "video_id": data["video_id"]
    }

    if collection.find_one(query) is None:
        collection.insert_one(data)
    else:
        new_graph = {"$set": {"graph": data["graph"], "conceptVocabulary": data["conceptVocabulary"]}}
        collection.update_one(query, new_graph)


def insert_conll_MongoDB(data):
    collection = db.conlls
    if collection.find_one({"video_id": data["video_id"]}) is None:
        collection.insert_one(data)


def insert_video(data):
    collection = db.videos
    if collection.find_one({"video_id": data["video_id"]}) is None:
        collection.insert_one(data)
    # else:
    #     new_graph = {"$set": {"extracted_keywords": data["extracted_keywords"]}}
    #     collection.update_one({"video_id": data["video_id"]}, new_graph)


def get_conll(video_id):
    collection = db.conlls
    if collection.find_one({"video_id":video_id}) is not None:
        return collection.find_one({"video_id":video_id})["conll"]
    else:
        return None


# from string id to object id
def get_user(user_string_id):
    user_id = ObjectId(user_string_id)
    return list(users.find({'_id': user_id}))[0]


def get_user_graphs(user):
    collection = db.graphs
    return list(collection.find({"annotator_id":user}))


def get_graph(user, video):
    collection = db.graphs
    return collection.find_one({"annotator_id":user, "video_id":video})["graph"]


def get_videos():
    collection = db.videos
    return list(collection.find({}).sort([("creator", pymongo.ASCENDING)]))


def get_graphs_info(selected_video=None):
    # If selected video is None
    # Returns all videos graphs, with the title, creator and the annotators
    # Else returns only the selected video

    collection = db.graphs

    pipeline = [

        # join con videos collection

        {
            "$lookup":{
                "from": "videos",
                "localField": "video_id",
                "foreignField": "video_id",
                "as": "video"
            }
        },

        {"$project":
            {
                "annotator_id": 1,
                "annotator_name": 1,
                "video_id": 1,
                "title": "$video.title",
                "creator": "$video.creator",
                "_id": 0}
         },

        {"$sort": {"creator": pymongo.ASCENDING}}
    ]

    aggregation = list(collection.aggregate(pipeline))
    graphs_info = {}

    for vid in aggregation:

        if "annotator_id" in vid:
            annotator = {"id": vid["annotator_id"], "name": vid["annotator_name"]}

            if vid["video_id"] not in graphs_info:
                graphs_info[vid["video_id"]] = {"title": vid["title"][0], "creator": vid["creator"], "annotators": [annotator]}
            else:
                graphs_info[vid["video_id"]]["annotators"].append(annotator)

    if selected_video is not None:
        if selected_video in graphs_info:
            return graphs_info[selected_video]
        else:
            return None

    return graphs_info


def get_concepts(annotator, video_id):
    collection = db.graphs

    pipeline = [
        {"$unwind": "$graph.@graph"},
        {
            "$match":
                {
                    "video_id": str(video_id),
                    "annotator_id": str(annotator),
                    "graph.@graph.type": "skos:Concept"
                }

        },

        {"$project":
            {
                "concept": "$graph.@graph.id",
                "_id": 0
            }
        }

    ]

    aggregation = collection.aggregate(pipeline)
    results = list(aggregation)
    concepts = []

    for concept in results:
        concepts.append(concept["concept"].replace("edu:","").replace("_"," "))

    return concepts


def get_concept_map(annotator, video_id):
    collection = db.graphs

    pipeline = [
        {"$unwind": "$graph.@graph"},
        {
            "$match":
                {
                    "video_id": str(video_id),
                    "annotator_id": str(annotator),
                    "graph.@graph.type": "oa:annotation",
                    "graph.@graph.motivation": "edu:linkingPrerequisite",
                }

        },

        {"$project":
            {
                "prerequisite": "$graph.@graph.body",
                "target": "$graph.@graph.target.dcterms:subject.id",
                "weight": "$graph.@graph.skos:note",
                "time": "$graph.@graph.target.selector.value",
                "sent_id": "$graph.@graph.target.selector.edu:conllSentId",
                "word_id": "$graph.@graph.target.selector.edu:conllWordId",
                "xywh": "$graph.@graph.target.selector.edu:hasMediaFrag",
                "creator": "$graph.@graph.dcterms:creator",
                "_id": 0
            }
        },

        {"$sort": {"time": 1}}

    ]

    aggregation = collection.aggregate(pipeline)
    concept_map = list(aggregation)

    for rel in concept_map:
        rel["prerequisite"] = rel["prerequisite"].replace("edu:","").replace("_"," ")
        rel["target"] = rel["target"].replace("edu:","").replace("_"," ")
        rel["weight"] = rel["weight"].replace("Prerequisite","")
        rel["time"] = rel["time"].replace("^^xsd:dateTime","")
        if "xywh" not in rel:
            rel["xywh"] = "None"
        if "word_id" not in rel:
            rel["word_id"] = "None"
        if "sent_id" not in rel:
            rel["sent_id"] = "None"

    return concept_map


def get_definitions(annotator, video_id):
    collection = db.graphs

    pipeline = [
        {"$unwind": "$graph.@graph"},
        {
            "$match":
                {
                    "video_id": str(video_id),
                    "annotator_id": str(annotator),
                    "graph.@graph.type": "oa:annotation",
                    "graph.@graph.motivation": "describing",
                }

        },

        {"$project":
            {
                "concept": "$graph.@graph.body",
                "start": "$graph.@graph.target.selector.startSelector.value",
                "end": "$graph.@graph.target.selector.endSelector.value",
                "start_sent_id": "$graph.@graph.target.selector.startSelector.edu:conllSentId",
                "end_sent_id": "$graph.@graph.target.selector.endSelector.edu:conllSentId",
                "creator": "$graph.@graph.dcterms:creator",
                "description_type": "$graph.@graph.skos:note",
                "_id": 0
            }
        },

        {"$sort": {"start": 1}}

    ]

    aggregation = collection.aggregate(pipeline)
    definitions = list(aggregation)

    for d in definitions:
        d["concept"] = d["concept"].replace("edu:","").replace("_"," ")
        d["end"] = d["end"].replace("^^xsd:dateTime","")
        d["start"] = d["start"].replace("^^xsd:dateTime", "")

    return definitions


def get_vocabulary(annotator, video_id):
    collection = db.graphs

    pipeline = [
        {"$unwind": "$conceptVocabulary.@graph"},
        {
            "$match":
                {
                    "video_id": str(video_id),
                    "annotator_id": str(annotator),
                    "conceptVocabulary.@graph.type": "skos:Concept"
                }
        },

        {"$project":
            {
                "prefLabel": "$conceptVocabulary.@graph.skos:prefLabel.@value",
                "altLabel": "$conceptVocabulary.@graph.skos:altLabel.@value",
                "_id": 0
            }
        }

    ]

    aggregation = collection.aggregate(pipeline)
    results = list(aggregation)

    # define new concept vocabulary
    conceptVocabulary = {}

    # if there is none on DB
    if len(results) == 0:
        return None

    # iterate for each concept and build the vocabulary basing on the number of synonyms
    for concept in results: 
 
        if "altLabel" in concept :
            if isinstance(concept["altLabel"], list):
                conceptVocabulary[concept["prefLabel"]] = concept["altLabel"]
            else:
                conceptVocabulary[concept["prefLabel"]] = [concept["altLabel"]]
        else:
            conceptVocabulary[concept["prefLabel"]]=[]

    return conceptVocabulary

'''
def get_vocabulary2(video_id, annotator_id, title=False):
    collection = db.graphs

    if collection.find_one({"video_id":video_id, "annotator_id": annotator_id}) is not None:
        video = collection.find_one({"video_id":video_id, "annotator_id": annotator_id})
        if title:
            return video["title"], video[""]

        return video["conceptVocabulary"]
    else:
        return None
'''

def get_segments_times(video_id):
    collection = db.videos

    if collection.find_one({"video_id":video_id}) is not None:
        video = collection.find_one({"video_id":video_id})
        return video["segment_starts"], video["segment_ends"]
    else:
        return None


def get_extracted_keywords(video_id, title=False):
    collection = db.videos

    if collection.find_one({"video_id":video_id}) is not None:
        video = collection.find_one({"video_id":video_id})
        if title:
            return video["title"], video["extracted_keywords"]

        return video["extracted_keywords"]
    else:
        return None

def remove_account(email):
    query = {"email": email}

    if users.find_one(query) is not None:
        try: 
            users.delete_one(query)
        except:
            return "Error"
        return "Done verified removed"
    elif unverified_users.find_one(query) is not None:
        try: 
            unverified_users.delete_one(query)
        except:
            return "Error"
        return "Done unverified removed"
    return "Not Found"

if __name__ == '__main__':

    #pprint(get_definitions("60d2e89014ff4217f4f50559", "sXLhYStO0m8"))
    print(remove_account('gabriele.romano121297@gmail.com'))
    print(remove_account('gaggioaxel@gmail.com'))
    print(remove_account('gaggioaxel@yahoo.it'))

    # collection = db.graphs
    # query = {
    #     "annotator_id": "60d2e89014ff4217f4f50559",
    #     "annotator_name": "Maria Rossi",
    #     "video_id": "sXLhYStO0m8"
    # }
    #
    #
    # new_graph = {"$set": {"graph": json["graph"]}}
    # collection.update_one(query, new_graph)
    # a = time.time()

    # curr_time = "00:07:40^^xsd:dateTime"
    # video_id = "sXLhYStO0m8"
    # annotator = "Pippo Topolino"
    #
    # pipeline = [
    #     {"$unwind": "$graph.@graph"},
    #     {
    #         "$match":
    #             {
    #                 "video_id": video_id,
    #                 "annotator": annotator,
    #                 "graph.@graph.type": "Annotation",
    #                 "graph.@graph.motivation": "describing",
    #                 "graph.@graph.target.selector.startSelector.value": {"$lte": curr_time},
    #                 "graph.@graph.target.selector.endSelector.value": {"$gte": curr_time}
    #             }
    #
    #     },
    #
    #     {"$project": {"concept":"$graph.@graph.body", "_id": 0}}
    #
    # ]
    # aggregation = db_graph.aggregate(pipeline)
    # results = list(aggregation)
    #
    # print("Concetti spiegati al tempo ", curr_time.split("^^")[0])
    # pprint(results)
    #
    # print("Tempo impiegato: ", time.time() - a, " secondi")
    # print()
    #
    # b = time.time()
    #
    # concept = "edu:ventral_arc"
    # curr_time = "00:02:00^^xsd:dateTime"
    #
    # pipeline = [
    #     {"$unwind": "$graph.@graph"},
    #     {
    #         "$match":
    #             {
    #                 "video_id": video_id,
    #                 "annotator": annotator,
    #                 "graph.@graph.type": "Annotation",
    #                 "graph.@graph.motivation": "linking",
    #                 "graph.@graph.target.dcterms:subject.id": concept,
    #                 "graph.@graph.target.selector.value": {"$lte": curr_time}
    #             }
    #
    #     },
    #
    #     {
    #         "$project": {
    #             "prerequisite": "$graph.@graph.body",
    #             "time": "$graph.@graph.target.selector.value",
    #             "_id": 0
    #         }
    #     }
    #
    #
    #
    #
    #
    # ]
    #
    # aggregation = db_graph.aggregate(pipeline)
    # prerequisites = list(aggregation)
    #
    #
    # print("\nPrerequisiti di " + concept)
    # pprint(prerequisites)
    #
    #
    # print("\nTempo impiegato: ", time.time() - b, " secondi")
    #
    # c = time.time()
    #
    # # mappa dei concetti
    # pipeline = [
    #     {"$unwind": "$graph.@graph"},
    #     {
    #         "$match":
    #             {
    #                 "video_id": video_id,
    #                 "annotator": "Luca Mirenda",
    #                 "graph.@graph.type": "Annotation",
    #                 "graph.@graph.motivation": "edu:linkingPrerequisite",
    #             }
    #
    #     },
    #
    #     {"$project":
    #          {
    #             "prerequisite": "$graph.@graph.body",
    #             "target": "$graph.@graph.target.dcterms:subject.id",
    #             "time": "$graph.@graph.target.selector.value",
    #             "_id": 0
    #          }
    #     },
    #
    #     {"$sort": {"time": 1}}
    #
    # ]
    #
    # aggregation = db_graph.aggregate(pipeline)
    # concept_map = list(aggregation)
    #
    # print("\nConcept map: ")
    # print(concept_map)
    #
    #
    # print("Tempo impiegato: ", time.time() - c, " secondi")
