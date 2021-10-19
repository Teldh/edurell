import db_mongo
import networkx as nx
import igraph
import agreement
from conllu import parse
#import pandas as pd
from pprint import pprint

#pip install python-igraph
#pip install pandas


class Graph:
    def __init__(self):
        self.graph = {}
        self.nodes = []

    def add_edge(self, u, v):

        if u not in self.nodes:
            self.nodes.append(u)
            self.graph[u] = []

        if v not in self.nodes:
            self.nodes.append(v)
            self.graph[v] = []

        self.graph[u].append(v)


def data_summary(annotator, video_id):
    concept_map = db_mongo.get_concept_map(annotator, video_id)

    unique_relations = []
    strong_relations = []
    weak_relations = []
    concepts = []

    G = nx.DiGraph()

    for rel in concept_map:

        G.add_edge(rel["prerequisite"], rel["target"])

        r = {"prerequisite":rel["prerequisite"], "target": rel["target"]}

        if r not in unique_relations:
            unique_relations.append(r)

        if rel["weight"] == "Strong":
            strong_relations.append(rel)
        else:
            weak_relations.append(rel)

        if rel["prerequisite"] not in concepts:
            concepts.append(rel["prerequisite"])

        if rel["target"] not in concepts:
            concepts.append(rel["target"])

    definitions = db_mongo.get_definitions(annotator, video_id)

    results = {"analysis_type": "data_summary", "concept_map": concept_map,
               "num_rels": len(concept_map), "num_weak": len(weak_relations),"num_strong": len(strong_relations),
               "num_unique": len(unique_relations), "num_definitions":len(definitions), "num_concepts": len(concepts),
               "num_transitives": len(detect_transitive_edges(G,10))}

    return results


def compute_agreement(user1, user2, video):
    concept_map1 = db_mongo.get_concept_map(user1, video)
    concept_map2 = db_mongo.get_concept_map(user2, video)
    words = []

    for rel in concept_map1:
        if rel["prerequisite"] not in words:
            words.append(rel["prerequisite"])

        if rel["target"] not in words:
            words.append(rel["target"])

    for rel in concept_map2:
        if rel["prerequisite"] not in words:
            words.append(rel["prerequisite"])

        if rel["target"] not in words:
            words.append(rel["target"])

    all_combs = agreement.createAllComb(words)

    # Calcolo agreement kappa no-inv all paths
    term_pairs = {user1: [], user2: []}
    term_pairs_tuple = {user1: [], user2: []}
    term_pairs[user1], all_combs, term_pairs_tuple[user1] = agreement.createUserRel(concept_map1, all_combs)
    term_pairs[user2], all_combs, term_pairs_tuple[user2] = agreement.createUserRel(concept_map2, all_combs)

    coppieannotate, conteggio = agreement.creaCoppieAnnot(user1, user2, term_pairs, all_combs, term_pairs_tuple)

    u1 = db_mongo.get_user(user1)
    u2 = db_mongo.get_user(user2)

    username1 = u1["name"] + " " + u1["surname"]
    username2 = u2["name"] + " " + u2["surname"]


    results = {"analysis_type": "agreement", "annotator1":username1, "annotator2": username2,
               "agreement":round(agreement.computeK(conteggio, all_combs), 3)}

    return results




def fleiss(video_id):

    users = db_mongo.get_graphs_info(video_id)["annotators"]

    words = []
    concept_maps = {}
    for user in users:
        concept_map = db_mongo.get_concept_map(user["id"], video_id)
        for rel in concept_map:
            if rel["prerequisite"] not in words:
                words.append(rel["prerequisite"])

            if rel["target"] not in words:
                words.append(rel["target"])

        concept_maps[user["id"]] = concept_map

    all_combs = agreement.createAllComb(words)

    term_pairs = {}
    for id in concept_maps:
        term_pairs[id] = agreement.createUserRel(concept_maps[id], all_combs)[0]

    #TODO se c'è un solo annotatore nel video va in errore
    try:
        fleiss = agreement.computeFleiss(term_pairs, all_combs)
    except:
        fleiss = 1

    return round(fleiss, 3)



def linguistic_analysis(annotator, video_id):
    concept_map = db_mongo.get_concept_map(annotator, video_id)

    conll = db_mongo.get_conll(video_id)
    #print(conll)
    parsed_conll = parse(conll)

    concepts = []

    for rel in concept_map:
        print(rel)
        rel["sentence"] = parsed_conll[int(rel["sent_id"])-1].metadata["text"]
        if rel["prerequisite"] not in concepts:
            concepts.append(rel["prerequisite"])

        if rel["target"] not in concepts:
            concepts.append(rel["target"])

    results = {"analysis_type": "linguistic","concept_map": concept_map, "concepts": concepts}

    return results


def detect_transitive_edges(graph, cutoff):
    '''
    Detect transitive relations manually inserted by the annotator.

    INPUT:
    graph
    cutoff: an int number of edges, after which the searching algorithm stops.

    OUTPUT
    A dict with transitives,
    indexed whether they have been manually inserted by the annotator
    or automatically detected in the graph by the search algorithm.
    '''

    transitives = []

    for source_node in graph.nodes():
        other_nodes = list(graph.nodes())
        other_nodes.remove(source_node)

        for target_node in other_nodes:
            paths = nx.all_simple_paths(graph, source_node, target_node, cutoff)

            for path in paths:
                if len(path) > 2 and graph.has_edge(source_node, target_node):
                    if (source_node, target_node) not in transitives:
                        transitives.append((source_node, target_node))

    return transitives

if __name__ == "__main__":

    # print(fleiss("sXLhYStO0m8"))
    # print(compute_agreement('60659634a320492e72f72598', '60659634a320492e72f72598', "sXLhYStO0m8"))

    # G = nx.DiGraph()
    # G.add_edge('a', 'c')
    # G.add_edge('a', 'b')
    # G.add_edge('a', 'd')
    # G.add_edge('b', 'd')
    # G.add_edge('c', 'd')


    # G_ig = igraph.Graph(directed=True)
    #
    # G_ig.add_vertices(['b','a', 'c', 'd' ,'e', 'x', 'z'])
    #
    # G_ig.add_edges([("a", 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'a'), ('z', 'x'), ('x', 'z')])

    pprint(data_summary("60d2e89014ff4217f4f50559", "sXLhYStO0m8"))

    # graph = {
    #     'a': ['b'],
    #     'b': ['c'],
    #     'c': ['d'],
    #     'd': ['e'],
    #     'e': ['a'],
    #     'x': ['z'],
    #     'z': ['x']
    # }

