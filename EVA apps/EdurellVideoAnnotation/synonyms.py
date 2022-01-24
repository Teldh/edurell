import copy
import nltk
from nltk.corpus import wordnet as wn
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF
from rdflib.namespace import FOAF, NamespaceManager
from rdflib.namespace import SKOS, XSD


#trovare i sinonimi da una lista di parole, ritorna un dizionario (keyword : lista sinonimi)
def get_synonyms_from_list(concepts): 
    synonyms=dict()


    keywords = copy.copy(concepts) # ricorda che word1 deve essere tutto minuscolo
    converter = lambda x: x.replace(' ', '_')
    keywords = list(map(converter, keywords))

    synonymsFound={}
    for starting_keyword in keywords:
        wordnetSynset1 = wn.synsets(starting_keyword)
        tempList1=[]
        synonymsFoundTemp=[]
        for synset1 in wordnetSynset1:
            for synWords1 in synset1.lemma_names():
                if(synWords1.lower() != starting_keyword.lower()):
                    tempList1.append(synWords1.lower())

        tempList1=list(set(tempList1))        
        
        for synonym in tempList1:
            for word in keywords:
                if (synonym==word):
                    synonymsFoundTemp.append(word.replace('_',' '))
        synonymsFoundTemp=list(set(synonymsFoundTemp))

        synonyms[starting_keyword.replace('_',' ')]=synonymsFoundTemp
    

    return synonyms 



#create skos dictionary
def create_skos_dictionary(synonyms):
    
    graph = Graph()
    skos = Namespace('http://www.w3.org/2004/02/skos/core#')
    graph.bind('skos', skos)
    uri_edurell = 'http://edurell.com/'


    for concept in synonyms.keys():
        
        uri_concept = URIRef(uri_edurell + 'Ann/' + concept.replace(" ", "_"))
        graph.add((uri_concept, RDF['type'], skos['Concept']))
        graph.add((uri_concept, skos['prefLabel'], Literal(concept, lang='en')))
        for synonym in synonyms[concept]:
            graph.add((uri_concept, skos['altLable'], Literal(synonym, lang='en')))


    graph.serialize(destination='output.txt', format='pretty-xml')


    #print graph.serialize(format='json-ld').decode('utf-8')


    return (graph)