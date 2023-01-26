import numpy as np
import pandas as pd
import nltk
from collections import defaultdict
from burst_kleinberg import kleinberg


class BurstExtractor:
    """
    A class for instantiating a Burst Extractor, i.e. an object that extract bursts from
    a text using Kleinberg's algorithm. See the example at the end of this description
    for further explanation.


    ### PARAMETERS ###
    ------------------
    To be passed to the constructor:

        1) text_filename (str): the name of the external file containing the text to analyze
        2) wordlist (list or str): the list of words for which we must detect bursts, either passed as a python list
                            or as a string representing the name of the external textfile that contains words.

    Variables generated by the class methods:

        3) rawtext (str): the unprocessed text found in textfile

        4) offsets (dict): the collection of offsets for each word, i.e. the indexes of all the
                            sentences where the word appears in the text. This data structure is a
                            dictionary of lists, where each word is assigned to a list of offsets:
                          {word1: [offset1, offset2, ...],
                           word2: [offset1, offset2, ...],
                           ...}
        5) bursts (pandas.DataFrame): a dataframe containing all the bursts detected by the algorithm.
                            Every row in the dataframe represents a burst, with a unique ID as index;
                            the dataframe has these columns:
                            ['keyword', 'level', 'start', 'end']


    ### METHODS ###
    ---------------
        1) find_offsets
        2) generate_bursts
        3) filter bursts
        4) get_excluded_words
    See the methods documentation for details.


    ### EXAMPLE ###
    ---------------
    burst_extr = BurstExtractor(text_filename="chapter4.txt",
                                wordlist="list_of_terms.txt")
    offsets = burst_extr.find_offsets()
    burst_extr.generate_bursts(s=1.05, gamma=0.0001)
    filtered_bursts = burst_extr.filter_bursts(level=1)
    """

    #def __init__(self, text_filename: str, wordlist: list or str):
    def __init__(self, text, wordlist):

        """
        Initializes the object from an external file containing the text and a python
        list containing the words (or an external textfile containing the words).

        :param text_filename: name of the file containing the book/chapter in plain text
        :param wordlist: (list or str) a python list containing the words. Alternatively,
                         the name of the file containing the words (one word for each line)
        """

        # TODO SE2020:
        """
            In origine il costruttore prendeva come input il nome del file txt contenente il testo. Questo perché in 
            effetti l'algoritmo di burst vuole come input un testo in cui trovare i burst, oltre che una lista
            di concetti per i quali trovare i burst. Ma nella versione a regime di PRET il file con il testo non serve 
            più, perché non c'è più bisogno di trovare le occorrenze dei concetti, queste DEVONO GIA' essere presenti 
            nel db. Controllare che sia effettivamente così e nel caso semplificare il codice.
            
            --> non è cosi, non ho le occorrenze dei concetti salvati nel db
        """

        # open and load the text into a variable
        '''self._text_filename = text_filename
        with open(text_filename, 'r', encoding='utf-8-sig') as file:
            self._rawtext = str(file.read())'''

        self._rawtext = text

        '''# build the terminology
        self._terminology = []
        # either from the list
        if type(wordlist) == list:
            self._terminology = wordlist[:]
            # filter out potential duplicates
            self._terminology = list(set(wordlist))

        # or from a file
        elif type(wordlist) == str:
            with open(wordlist, 'r', encoding='utf8') as file:
                for word in list(file.read().split('\n')):
                    # append only once
                    if word not in self._terminology:
                        self._terminology.append(word)
        else:
            raise ValueError("""The argument for 'wordlist' must be either a list 
                                or a string representing the name of the file.""")'''

        self._terminology = wordlist

        # initialize parameters of Kleinberg
        self._s = None
        self._gamma = None
        # initialize the final structures
        self._offsets = defaultdict(list)
        self._bursts = pd.DataFrame(columns=['keyword', 'level', 'start', 'end'],
                                    dtype='int64')

    def find_offsets(self, words=None, occ_index_file: str=None) -> dict or defaultdict:
        """
        Determine the offsets (i.e. occurrences) in the text for all the words belonging to
        the wordlist. This can be done either by relying on precomputed offsets stored in a
        csv file, or by finding them in the text when no such precomputed values are given.

        :param occ_index_file df with the following columns:

                            "Lemma"    "idFrase"    "idParolaStart"

                            If no value is passed, offsets will be found in the text using
                            NLTK text processing tools.

        :return: offsets: a dictionary of lists, where each word (the key) is assigned to the
                            indexes of the sentences where the word appears. The results will
                            be automatically used in the method 'generate_bursts' to detect the
                            periods of bursting activity.
        """

        if occ_index_file is not None:
            ### use offsets that are available in occ index file
            self._offsets = {}

            for o in occ_index_file.itertuples():
                if o.Lemma not in self._offsets:
                    self._offsets[o.Lemma] = []

                if o.idFrase not in self._offsets[o.Lemma]:
                    self._offsets[o.Lemma].append(o.idFrase)

            # sents_idx = pd.read_csv(occ_index_file, index_col=0,
            #                         usecols=["Lemma", "idFrase", "idParolaStart"],
            #                         encoding="utf-8", sep="\t")

            # reset and populate the offsets dict
            # self._offsets = {}
            # for t in sents_idx.index.unique():
            #     if type(sents_idx.loc[t]) == pd.Series:
            #         # has only one occurrence
            #         self._offsets[t] = [sents_idx.loc[t]['idFrase']]
            #     elif type(sents_idx.loc[t]) == pd.DataFrame:
            #         # has more than one occurrence
            #         # use a set, because Kleinberg does not accept events occurring at the same time
            #         self._offsets[t] = sorted(list(set((sents_idx.loc[t]['idFrase'].tolist()))))

        else:
            ### find the offsets using NLTK
            # (non dovrebbe mai servire)

            # reset and populate the offsets dict
            self._offsets = defaultdict(list)

            sentences = nltk.sent_tokenize(self._rawtext)
            # search each word in each sentence
            for word in self._terminology:
                for index, sent in enumerate(sentences):
                    if word.upper() in sent.upper():
                        # add the index of the sentence in the list of offsets of that word
                        self._offsets[word].append(index)
        return self._offsets

    def generate_bursts(self, s=2, gamma=1) -> pd.DataFrame or None:
        """
        Computes the bursts and store them in a dataframe.

        :param s: (float) the base of the exponential distribution (must be greater than 1)
        :param gamma: (float) the coefficient of the costs between states (must be positive)
        :return: bursts_df: a dataframe containing all the burst detected by the algorithm.
                            Every row in the dataframe represents a burst; the columns are
                            ['keyword', 'level', 'start', 'end'].
        """

        if not self._offsets:
            choice = input("""You must first detect the offsets (by calling the method 'find_offset').
                            Do you want to find offsets now (without an index file) 
                            and then automatically detect the bursts? Press y/n\n""")
            if choice in ['y', 'Y']:
                print('The offsets will be detected and then the process will compute bursts.\n')
                self._offsets = self.find_offsets()
            else:
                print("Neither offsets or bursts will be computed.\n")
                return None

        # reset self._burst
        self._bursts = pd.DataFrame(columns=['keyword', 'level', 'start', 'end'],
                                    dtype='int64')

        for keyword in self._offsets:
            # compute bursts
            curr_bursts = kleinberg(self._offsets[keyword], s, gamma)
            # insert the name of the word in the array
            curr_bursts = np.insert(curr_bursts, 0, values=keyword, axis=1)
            # convert it to a df and append it to the complete df of bursts
            curr_bursts_df = pd.DataFrame(curr_bursts,
                                          columns=['keyword', 'level', 'start', 'end'])
            self._bursts = pd.concat([self._bursts, curr_bursts_df], ignore_index=True)

        # save parameters of Kleinberg (they are needed for 'plot_bursts')
        #self._s = s
        #self._gamma = gamma

        return self._bursts

    def filter_bursts(self, level=1, save_monolevel_keywords=False, replace_original_results=False) -> pd.DataFrame or None:
        """
        Returns a dataframe containing only the bursts with the desired level.

        :param level: (int, by default 1) level inside the burstiness hierarchy
        :param save_monolevel_keywords:
        :param replace_original_results:
        :return: a dataframe containing only the bursts with the desired level.
        """

        if self._bursts.shape[0] == 0:
            raise ValueError("Bursts non yet extracted: "
                             "call the method 'generate_bursts' first!")

        # avoid index errors
        if level < 0:
            raise ValueError("The level must have a positive value.")
        if level > self._bursts['level'].max():
            print("""The desired level exceeds the maximum level present in the results:
                    the latter will be used.""")
            level = self._bursts['level'].max()

        b = self._bursts.copy()

        if save_monolevel_keywords:
            # don't filter the terms with only a burst, even if this is less that the desired
            for t in b["keyword"].unique().tolist():
                if b[b["keyword"] == t].shape[0] == 1:
                    i = b.index[b['keyword'] == t][0]
                    b.at[i, "level"] = 1

        filtered = b.where(b['level'] == level).dropna()

        if replace_original_results:
            self._bursts = filtered.copy()
        else:
            return filtered

    def break_bursts(self, burst_length=30, num_occurrences=3, replace_original_results=False, verbose=False):
        """
        Finds excessively long burst and breaks them down in smaller bursts of length=1.
        Example: a burst with start=168 and end=602 associated to a term that only
                 occurs in sentences 168 and 602 will be deleted and two bursts (with
                 limits 168-168 and 602-602) will be added.

        :param burst_length: defines what "excessively long" should mean. Bursts with
                    length >= this parameter will be handled.
        :param num_occurrences: burst of a term with number of occurrences <= this
                    parameter will be handled
        :param replace_original_results:
        :param verbose: (bool, default False) If True, the method will print the ids
                    start, end of deleted burst, as well as the name of the associated
                    term and its occurrences in the text.
        :return:
        """

        if verbose:
            print("The following burst have been deleted and replaced with smaller bursts:\n")

        b = self._bursts.copy()

        for i, row in self._bursts.iterrows():
            curr_len = (row["end"] - row["start"]) + 1
            if curr_len >= burst_length and len(self._offsets[row["keyword"]]) <= num_occurrences:

                b.drop(i, inplace=True)
                last_idx = b.index[-1]
                b.loc[last_idx + 1] = {"keyword": row["keyword"], "level": row["level"],
                                       "start": row["start"], "end": row["start"]}
                b.loc[last_idx + 1] = {"keyword": row["keyword"], "level": row["level"],
                                       "start": row["end"], "end": row["end"]}

                if verbose:
                    print(row["keyword"], "\toffsets:", self._offsets[row["keyword"]],
                          "\tstart:", int(row["start"]), "\tend:", int(row["end"]), "\n")

        if replace_original_results:
            self._bursts = b.copy()
        else:
            return b


    def get_words_with_bursts(self, level=1) -> set:
        """
        Returns the set of words for which the algorithm has detected
        at least a burst activity with the level passed as an argument.

        :param level: (int, by default 1) level inside the burstiness hierarchy
        :return: a set of strings
        """

        filtered_burst = self.filter_bursts(level)

        return set(filtered_burst['keyword'].unique())

    def get_excluded_words(self, level=1) -> set:
        """
        Returns the set of words for which the algorithm has not detected
        any burst activity with the level passed as an argument.

        :param level: (int, by default 1) level inside the burstiness hierarchy
        :return: a set of strings
        """

        filtered_burst = self.filter_bursts(level)

        return set(self._terminology) - set(filtered_burst['keyword'].unique())

    @property
    def text_filename(self):
        """Getter of the name of the file containing the input text"""
        return self._text_filename

    @property
    def rawtext(self):
        """Getter of the raw text as a string"""
        return self._rawtext

    @property
    def terminology(self):
        """Getter of the list of terms"""
        return self._terminology

    @property
    def offsets(self):
        """Getter of the offsets"""
        return self._offsets

    @property
    def bursts(self):
        """Getter of the bursts"""
        return self._bursts

    def __repr__(self):
        return 'BurstExtractor(text_filename={0}, wordlist={1})'.format(
            repr(self._text_filename), repr(self._terminology))
