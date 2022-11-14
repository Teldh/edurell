from rdflib import Graph, URIRef, RDF, BNode, ConjunctiveGraph, Namespace
from rdflib.namespace import SKOS, XSD
from rdflib.term import Literal
from rdflib.serializer import Serializer

import json
import pyld
import time
from datetime import datetime
import db_mongo


oa = Namespace("http://www.w3.org/ns/oa#")
dctypes = Namespace("http://purl.org/dc/dcmitype/")
dcterms = Namespace("http://purl.org/dc/terms/")
edu = Namespace("http://edurell.com/")

edurell = "http://edurell.com/"
#context = "http://www.w3.org/ns/anno.jsonld"
context = ["http://www.w3.org/ns/anno.jsonld", {"edu": edurell}]


def create_graph_jsonld(annotations, isGoldCreation=False, isBurst=False):

    concepts_anno = annotations["definitions"]
    prereq_anno = annotations["relations"]
    video_id = annotations["id"]

    if not isGoldCreation and not isBurst:
        creator = annotations["annotator"]
        creator = Literal(creator)

    g = Graph()

    g.bind("oa", oa)
    g.bind("dctypes", dctypes)
    g.bind("edu", edu)
    g.bind("SKOS", SKOS)
    g.bind("dcterms", dcterms)


    video = URIRef(edurell + "video_" + str(video_id))
    g.add((video, RDF.type, dctypes.movingImage))

    conll = URIRef(edurell + "conll_" + str(video_id))
    g.add((conll, RDF.type, dctypes.text))


    # collegamento video conll
    ann_linking_conll = URIRef(edurell + "ann0")
    g.add((ann_linking_conll, RDF.type, oa.annotation))
    g.add((ann_linking_conll, oa.motivatedBy, edu.linkingConll))
    g.add((ann_linking_conll, oa.hasBody, conll))
    g.add((ann_linking_conll, oa.hasTarget, video))

    date = Literal(datetime.now())


    # per ogni annotazione di concetto spiegato aggiungo le triple
    for i, annotation in enumerate(concepts_anno):
        ann = URIRef(edurell + "ann" + str(i + 1))

        g.add((ann, RDF.type, oa.annotation))

        if isGoldCreation or isBurst:
            g.add((ann, dcterms.creator, Literal(annotation["creator"])))
        else:
            g.add((ann, dcterms.creator, creator))

        g.add((ann, dcterms.created, date))
        g.add((ann, oa.motivatedBy, oa.describing))
        g.add((ann, SKOS.note, Literal(annotation["description_type"])))


        concept = URIRef(edurell + annotation["concept"].replace(" ", "_"))

        g.add((concept, RDF.type, SKOS.Concept))
        g.add((ann, oa.hasBody, concept))

        blank_target = BNode()
        blank_selector = BNode()

        g.add((ann, oa.hasTarget, blank_target))
        g.add((blank_target, RDF.type, oa.specificResource))

        g.add((blank_target, oa.hasSelector, blank_selector))
        g.add((blank_selector, RDF.type, oa.rangeSelector))

        blank_startSelector = BNode()
        blank_endSelector = BNode()

        g.add((blank_startSelector, RDF.type, edu.InstantSelector))
        g.add((blank_endSelector, RDF.type, edu.InstantSelector))

        g.add((blank_selector, oa.hasStartSelector, blank_startSelector))
        g.add((blank_selector, oa.hasEndSelector, blank_endSelector))

        g.add((blank_startSelector, RDF.value, Literal(annotation["start"] + "^^xsd:dateTime")))
        g.add((blank_startSelector, edu.conllSentId, Literal(annotation["start_sent_id"])))
        #g.add((blank_startSelector, edu.conllWordId, Literal(annotation["word_id"])))

        g.add((blank_endSelector, RDF.value, Literal(annotation["end"] + "^^xsd:dateTime")))
        g.add((blank_endSelector, edu.conllSentId, Literal(annotation["end_sent_id"])))


        g.add((blank_target, oa.hasSource, video))

    num_definitions = len(concepts_anno) + 1

    # per ogni annotazione di prerequisito aggiungo le triple
    for i, annotation in enumerate(prereq_anno):
        ann = URIRef(edurell + "ann" + str(num_definitions + i))

        target_concept = URIRef(edurell + annotation["target"].replace(" ", "_"))
        prereq_concept = URIRef(edurell + annotation["prerequisite"].replace(" ", "_"))

        g.add((target_concept, RDF.type, SKOS.Concept))
        g.add((prereq_concept, RDF.type, SKOS.Concept))

        g.add((ann, RDF.type, oa.annotation))

        if isGoldCreation or isBurst:
            g.add((ann, dcterms.creator, Literal(annotation["creator"])))
        else:
            g.add((ann, dcterms.creator, creator))

        g.add((ann, dcterms.created, date))
        g.add((ann, oa.motivatedBy, edu.linkingPrerequisite))

        g.add((ann, oa.hasBody, prereq_concept))
        g.add((ann, SKOS.note, Literal(annotation["weight"] + "Prerequisite")))

        blank_target = BNode()

        g.add((ann, oa.hasTarget, blank_target))
        g.add((blank_target, RDF.type, oa.specificResource))
        g.add((blank_target, dcterms.subject, target_concept))

        g.add((blank_target, oa.hasSource, video))

        blank_selector_video = BNode()

        g.add((blank_target, oa.hasSelector, blank_selector_video))
        g.add((blank_selector_video, RDF.type, edu.InstantSelector))
        g.add((blank_selector_video, RDF.value, Literal(annotation["time"] + "^^xsd:dateTime")))

        if annotation["xywh"] != "None":
            g.add((blank_selector_video, edu.hasMediaFrag, Literal(annotation["xywh"])))


        g.add((blank_selector_video, edu.conllSentId, Literal(annotation["sent_id"])))

        if annotation["word_id"] != "None":
            g.add((blank_selector_video, edu.conllWordId, Literal(annotation["word_id"])))

    # stampo il grafo in formato turtle
    # turtle = g.serialize(format='turtle').decode("utf-8")
    # print(turtle)

    # creo file json-ld

    #jsonld = json.loads(g.serialize(format='json-ld', context=context))

    jsonld = json.loads(g.serialize(format='json-ld'))
    jsonld = pyld.jsonld.compact(jsonld, context)

    '''
    Nested nodes creation
    
    FROM:                            |  TO:
    {                                |  {
        ...                          |    ...
        "target": 123                |     "target":{
    },                               |                 "id":123,
    {                                |                  "type":example
        "id": 123,                   |               }
        "type": example              |   }
    }
    
    '''

    for o in jsonld["@graph"]:
        if "target" in o:
            for i, t in enumerate(jsonld["@graph"]):
                if o["motivation"] != "edu:linkingConll" and o["target"] == t["id"]:
                    o["target"] = t
                    del jsonld["@graph"][i]
                    for j, s in enumerate(jsonld["@graph"]):
                        if o["target"]["selector"] == s["id"]:
                            o["target"]["selector"] = s
                            del jsonld["@graph"][j]

                            if o["motivation"] == "describing":
                                for k, p in enumerate(jsonld["@graph"]):
                                    if o["target"]["selector"]["startSelector"] == p["id"]:
                                        o["target"]["selector"]["startSelector"] = p
                                        del jsonld["@graph"][k]
                                        break

                                for k, p in enumerate(jsonld["@graph"]):
                                    if o["target"]["selector"]["endSelector"] == p["id"]:
                                        o["target"]["selector"]["endSelector"] = p
                                        del jsonld["@graph"][k]
                                        break


    #pprint(jsonld)
    data = {
        "graph":jsonld
    }

    #print(data)

    return g, data


# transform the jsonld graph back to rdflib
def graph_to_rdf(jsonld):
    json_expanded = pyld.jsonld.expand(jsonld)

    return Graph().parse(data=json.dumps(json_expanded), format='json-ld')


if __name__ == '__main__':

    json_graph = db_mongo.get_graph("616726e4d1a3488902b4b55d", "sXLhYStO0m8")

    print(json_graph)
    json_expanded = pyld.jsonld.expand(json_graph)

    gr = Graph()\
        .parse(data=json.dumps(json_graph), format='json-ld')

    tic = time.time()

    # Seleziona i concetti che sono spiegati nel video
    query1 = """
        PREFIX oa: <http://www.w3.org/ns/oa#>
        PREFIX edu: <http://edurell.com/>
        SELECT ?explained_concept
           WHERE {
                ?concept_annotation oa:motivatedBy oa:describing.
                ?concept_annotation oa:hasBody ?explained_concept.
            }"""

    qres = gr.query(query1)

    toc = time.time()

    print("Results: - obtained in %.4f seconds" % (toc - tic))
    for row in qres:
        print("%s" % row)

    print()