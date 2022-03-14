#------------------------------------------------------------------
# Class for evaluating prerequisite relationship using temporal
# patterns
#
# Author: sampas85
# Integrated in EDURELL by Luca Mirenda
#------------------------------------------------------------------
import pandas as pd

from burst_extractor import BurstExtractor
from burst_weight_assigner import WeightAssigner
from burst_weight_normalizer import WeightsNormalizer
import burst_results_processor as burst_proc
from audio_transcription import speech_from_youtube
import sys
import copy
from conllu import parse
from conll import lemmatize, get_text
import agreement
from segmentation import get_timed_sentences
from nltk import tokenize
import datetime
from nltk import WordNetLemmatizer

def burst_extraction(video_id, concepts, n=90):

    text, conll = get_text(video_id, return_conll=True)
    text = text.replace("-", " ")

    concept_map_burst, burst_definitions = Burst(text, concepts, video_id, conll, threshold=0.7,
                                                 top_n=n, max_gap=1).launch_burst_analysis()

    return concept_map_burst, burst_definitions

# Get mapping of concepts and synonyms to selected word (alphabetically)
def get_synonyms_mappings(conceptVocabulary):
    
    syn_map = {}
    new_concepts = []

    # get unique id for each syn set
    for concept in conceptVocabulary:
        synset = [concept]
        synset = synset + conceptVocabulary[concept]
        synset.sort()
        syn_map[concept] = synset[0]
        new_concepts.append(synset[0])

    new_concepts = list(set(new_concepts))
    
    return syn_map, new_concepts

def burst_extraction_with_synonyms(video_id, concepts, conceptVocabulary, n=90):

    text, conll = get_text(video_id, return_conll=True)
    text = text.replace("-", " ")

    syn_map, new_concepts = get_synonyms_mappings(conceptVocabulary)

    concept_map_burst, burst_definitions = Burst(text, new_concepts, video_id, conll, syn_map, threshold=0.7,
                                                 top_n=n, max_gap=1).launch_burst_analysis()

    return concept_map_burst, burst_definitions

class Burst:

    def __init__(self, text, words, video_id, conll, syn_map=False, threshold=0,  top_n=None, s=1.05, gamma=0.0001, level=1, allen_weights=None,
                 use_inverses=False, max_gap=4, norm_formula="modified"):#occ, f,
        self.text = text
        self.words = words

        self.conll = parse(conll)
        self.video_id = video_id
        self.threshold = threshold
        self.top_n = top_n


        #Kleinberg's parameters
        self.S = s
        self.GAMMA = gamma
        self.LEVEL = level

        # #self.occurences
        # #Dataframe contentente le colonne "Lemma", "idFrase", "idParolaStart"
        occurrences_index = []
        self.first_occurence = {}

        '''
        PHASE 0
        Initialize self.occurrences that contains every word and their positions in the conll's sentences
        '''

        max_word_lenght = 0

        for w in self.words:
            l = len(w.split(" "))
            if l > max_word_lenght:
                max_word_lenght = l

        upper_words = [x.upper() for x in self.words]
        lemmatizer = WordNetLemmatizer()


        for sent in self.conll:
            sent_index = int(sent.metadata["sent_id"])-1
            conll_words = self.conll[sent_index].filter(upos=lambda x: x != "PUNCT")

            for i_, word in enumerate(conll_words):

                word_index = int(word["id"])
                words = word["lemma"]
                words_form = word["form"]
                nltk_lemmatized = lemmatizer.lemmatize(word["form"])

                for i in range(1, max_word_lenght+1):

                    occ_words = ""
                    # cerco occorrenza della parola nella forma base, lemmatizata con la conll e lematizzata con nltk
                    if words.upper() in upper_words:
                        occ_words = words.lower()
                    elif words_form.upper() in upper_words:
                        occ_words = words_form.lower()
                    elif nltk_lemmatized.upper() in upper_words:
                        occ_words = nltk_lemmatized

                    if occ_words != "":
                        if occ_words not in self.first_occurence:
                            self.first_occurence[occ_words] = sent_index

                        d = [occ_words, sent_index, word_index]
                        occurrences_index.append(d)

                    if i + i_ < len(conll_words):
                        words += " " + conll_words[i_ + i]["lemma"]
                        words_form += " " + conll_words[i_ + i]["form"]
                        nltk_lemmatized += " " + lemmatizer.lemmatize(conll_words[i_ + i]["form"])
                    else:
                        break

        
        if syn_map == False:
            self.occurrences = pd.DataFrame(data=occurrences_index, columns=["Lemma", "idFrase", "idParolaStart"])
        else:
            occur = pd.DataFrame(data=occurrences_index, columns=["Lemma", "idFrase", "idParolaStart"])
            new_occur = []
            for o in occur.itertuples(): 
                new_occur.append([syn_map[o.Lemma], o.idFrase, o.idParolaStart])
            self.occurrences = pd.DataFrame(new_occur, columns=['Lemma', 'idFrase', 'idParolaStart'])


        # weights for Allen and type of normalization formula
        if allen_weights is None:
            self.ALLEN_WEIGHTS = {'equals': 2, 'before': 5, 'after': 0, 'meets': 3, 'met-by': 0,
                             'overlaps': 7, 'overlapped-by': 1, 'during': 7, 'includes': 7,
                             'starts': 4, 'started-by': 2, 'finishes': 2, 'finished-by': 8}
        else:
            self.ALLEN_WEIGHTS = allen_weights


        self.USE_INVERSES = use_inverses
        self.MAX_GAP = max_gap
        self.NORM_FORMULA = norm_formula

        # decide if preserve relations when giving direction to the burst matrix
        self.PRESERVE_RELATIONS = True



    def launch_burst_analysis(self):
        """Launch Burst analysis"""
        try:
            # FIRST PHASE: extract bursts
            #print("Extracting bursts...\n")

            #print("text")
            #print(self.text)
            #print("words")
            #print(self.words)
            #print("occurrences")
            #print(self.occurrences[0:50])

            burst_extr = BurstExtractor(text=self.text, wordlist=self.words)
            burst_extr.find_offsets(words=self.words, occ_index_file=self.occurrences)
            burst_extr.generate_bursts(s=self.S, gamma=self.GAMMA)
            burst_extr.filter_bursts(level=self.LEVEL, save_monolevel_keywords=True, replace_original_results=True)
            burst_extr.break_bursts(burst_length=30, num_occurrences=3, replace_original_results=True)
            burst_res = burst_extr.bursts

            if burst_res.empty:
                raise ValueError("The chosen parameters do not produce results")

            # obtain json with first, last, ongoing, unique tags
            # bursts_json = burst_proc.get_json_with_bursts(burst_res, self.occurrences)



            # SECOND PHASE: detect relations between bursts and assign weights to them
            #print("Detecting Allen's relations and assign weights to burst pairs...\n")
            weight_assigner = WeightAssigner(bursts=burst_res,
                                             relations_weights=self.ALLEN_WEIGHTS)
            weight_assigner.detect_relations(max_gap=self.MAX_GAP, alpha=0.05, find_also_inverse=self.USE_INVERSES)
            # output data for the gantt interface and ML projects
            burst_pairs_df = weight_assigner.burst_pairs

            bursts_weights = weight_assigner.bursts_weights


            # THIRD PHASE: normalize the bursts' weights
            #print("Normalizing the matrix with weights of burst pairs...\n")
            weight_norm = WeightsNormalizer(bursts=burst_res,
                                            burst_pairs=burst_pairs_df,
                                            burst_weight_matrix=bursts_weights)
            weight_norm.normalize(formula=self.NORM_FORMULA, occ_index_file=self.occurrences)

            burst_norm = weight_norm.burst_norm.round(decimals=6)


            # FINAL STEP: give directionality to bursts
            #print("Giving directionality to the concept matrix built with bursts...\n")

            directed_burst = burst_proc.give_direction_using_first_burst(undirected_matrix=burst_norm,
                                                                         bursts_results=burst_res,
                                                                         indexes=self.occurrences,
                                                                         level=self.LEVEL, preserve_relations=self.PRESERVE_RELATIONS)

            # add rows and columns in the matrices for possible discarded terms
            #print("\nAdding rows and columns for missing concepts in the burst matrix...\n")
            missing_terms = [term for term in self.words
                             if term not in directed_burst.index]

            for term in missing_terms:
                directed_burst.loc[term] = 0
                directed_burst[term] = 0

            #print("Shape of final directed burst matrix:", directed_burst.shape)

            # get an edgelist with the extracted prerequisite relations
            #print("Getting an edgelist with the extracted prerequisite relations...\n")
            sorted_edgelist = pd.DataFrame(burst_proc.to_edgelist(directed_burst),
                                           columns=["prerequisite", "target", "weight"])


            return self.df_to_data(sorted_edgelist, burst_res, use_conll=True)

        except ValueError as e:
            print("error:", sys.exc_info())
            #self.updateStatus("failed")
            raise e




    def df_to_data(self, sorted_edgelist, burst_res, use_conll=False):
        ''' Transform burst dataframe results in data '''

        concept_map = []
        definitions = []

        subtitles, autogenerated = speech_from_youtube("https://www.youtube.com/watch?v=" + self.video_id)
        if not use_conll:
            sentences = tokenize.sent_tokenize(self.text)
        else:
            sentences = [sent.metadata["text"] for sent in self.conll]

        timed_sentences = get_timed_sentences(subtitles, sentences)

        if self.top_n is not None:
            sorted_edgelist = sorted_edgelist.head(self.top_n)

        for rel in sorted_edgelist.itertuples():
            if self.threshold < rel.weight:

                if self.first_occurence[rel.prerequisite] > self.first_occurence[rel.target]:
                    sent_id = self.first_occurence[rel.prerequisite]
                else:
                    sent_id = self.first_occurence[rel.target]

                a = {"prerequisite": rel.prerequisite,
                     "target": rel.target,
                     "creator": "Burst Analysis",
                     "weight": "Strong",
                     "time": str(datetime.timedelta(seconds=timed_sentences[sent_id]["start"])),
                     "sent_id": sent_id,
                     "xywh": "None",
                     "word_id": "None",
                     "weight_burst":rel.weight
                     }
                if a not in concept_map:
                    concept_map.append(a)

        concept_longest_burst = {}

        for d in burst_res.itertuples():
            burst_len = d.end - d.start
            if d.keyword not in concept_longest_burst:
                concept_longest_burst[d.keyword] = burst_len

            elif burst_len > concept_longest_burst[d.keyword]:
                concept_longest_burst[d.keyword] = burst_len

        for d in burst_res.itertuples():
            if d.end - d.start > 1:

                if concept_longest_burst[d.keyword] == d.end - d.start:
                    descr_type = "Definition"
                else:
                    descr_type = "In Depth"

                definitions.append({
                    "concept": d.keyword,
                    "start_sent_id": d.start,
                    "end_sent_id": d.end,
                    "start": str(datetime.timedelta(seconds=timed_sentences[d.start]["start"])),
                    "end": str(datetime.timedelta(seconds=timed_sentences[d.end]["end"])),
                    "description_type": descr_type,
                    "creator": "Burst Analysis"
                })

        return concept_map, definitions


def compute_agreement_burst(concept_map1, concept_map2):

    words = []
    user1 = "gold"
    user2 = "burst"

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


    results = {"analysis_type": "agreement",
               "agreement":round(agreement.computeK(conteggio, all_combs), 3)}

    return results



