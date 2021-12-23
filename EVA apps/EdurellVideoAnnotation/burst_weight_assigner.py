import pandas as pd
from burst_extractor import BurstExtractor


class WeightAssigner:
    """
    A class to detect relations between bursts and assign weights to these relations based on Allen's algebra.


    ### PARAMETERS ###
    ------------------
    To be passed to the constructor:

        1) bursts (pandas.DataFrame): a dataframe containing the bursts. Every row must represents a
                            burst (with a unique ID as index). The dataframe must have the columns:
                            ['keyword', 'start', 'end'].
                            The more natural value for this input is the dataframe stored in a
                            BurstExtractor object, that is generated after calling the method
                            'BurstExtractor.generate_bursts(s, gamma)'

                            To directly build a WeightAssigner from a BurstExtractor, use the class method:
                            'from_burst_extractor(fitted_burst_extractor, relations_weights, level)'

        2) relations_weights (dict): a dictionary that associates a weight to every relation in Allen's
                            algebra. The key-set must contain all the relations' names (inverse relations
                            included):

                            'equals', 'before', 'after', 'meets', 'met-by', 'overlaps', 'overlapped-by',
                            'during', 'includes', 'starts', 'started-by', 'finishes', 'finished-by'.

                            If no dict is passed, the predefined weights will be used.

        3) text_filename (str, optional): the name of the file containing the book/chapter in plain text.

    Generated by the class methods:

        4) burst_matrix: a Pandas.dataFrame consisting of a square matrix of burst weights
                            (i.e., dimension = num_bursts x num_bursts).
                            Rows and columns have as labels the IDs of the bursts.

        5) burst_pairs: a dataframe storing all the detected pairs of Allen-related bursts, in a suitable
                    format for machine learning projects ond gantt interface (i.e. without weights, that
                    are not needed or will be eventually learned). For two given concepts x and y with at
                    least a burst Bx related to a burst By, columns are:
                    ['x', 'y', 'Bx_id', 'By_id', 'Bx_start', 'Bx_end', 'By_start', 'By_end', 'Rel']

    ### METHODS ###
    ---------------
    Public:
        1) detect_relations

    Private helpers:
        2) _initialize_dataframes
        3) _prop_tol_gap
        4) _store_weights
        5~17) _equals, _finishes, etc.

    See the methods documentation for details.

    ### EXAMPLE ###
    ---------------
    weight_assigner = WeightAssigner(bursts=filtered_bursts,
                                     relations_weights=rel_w,
                                     text_filename="chapter4.txt")
    weight_assigner.detect_relations()
    burst_pairs = weight_assigner.burst_pairs
    bursts_weights = weight_assigner.bursts_weights.dataframe
    """

    # predefined weights (they also include inverse relations)
    RELATIONS_WEIGHTS = {'equals': 5, 'before': 2, 'after': 0, 'meets': 3, 'met-by': 0,
                         'overlaps': 8, 'overlapped-by': 1, 'during': 7, 'includes': 7,
                         'starts': 6, 'started-by': 2, 'finishes': 2, 'finished-by': 8}

    def __init__(self, bursts: pd.DataFrame, relations_weights: dict = None):
        """
        Initializes the object from a dataframe storing the concepts' bursts in a
        text (this can be extracted by a BurstExtractor) and a dictionary containing
        the weights for Allen's algebra's relations.

        :param bursts: a dataframe possibly generated by a BurstExtractor.
        :param relations_weights: a dict containing weights associated to every possible relation.
                        (if no dictionary is passed, the predefined weights will be used)
        """

        self._bursts = bursts
        self._relations_weights = relations_weights or self.RELATIONS_WEIGHTS

        # initialize the two final data structures
        self._initialize_dataframes()

    @classmethod
    def from_burst_extractor(cls, fitted_burst_extractor: BurstExtractor,
                             relations_weights: dict = None, level: int = 1):
        """
        Initializes the object from a BurstExtractor object.

        :param fitted_burst_extractor: a BurstExtractor object with already computed bursts.
        :param relations_weights: a dictionary with weights for Allen's algebra.
        :param level: the level of bursts (default=1)
        :return:
        """

        bursts = fitted_burst_extractor.filter_bursts(level)

        return cls(bursts, relations_weights)

    def _initialize_dataframes(self) -> None:
        """
        Initialize the final data structures as empty dataframes or reset them to empty.
        """

        # initialize the final square matrix of weights
        self._burst_matrix = pd.DataFrame(0.0,
                                          index=self._bursts.index.tolist(),
                                          columns=self._bursts.index.tolist())

        # initialize the dataset for the machine learning project and for gantt interface
        self._burst_pairs = pd.DataFrame(columns=['x', 'y',
                                                  'Bx_id', 'By_id',
                                                  'Bx_start', 'Bx_end',
                                                  'By_start', 'By_end',
                                                  'Rel'])

    def detect_relations(self, max_gap=10, alpha=0.05, find_also_inverse=False):
        """
        Detects which relations exists between bursts, computes the weight according
        to the relations_weights schema and store it in the final data structure.

        :param max_gap: (int) A maximum number of sentences between two bursts after
                        which no relation will be assigned (by default: 10). It is used
                        to reduce the number of 'before' and 'after' relations).
        :param alpha: (float) proportionality coefficient (by default: 0.05). It is
                        multiplied by the total length of the two bursts.
        :param find_also_inverse: (bool) By default False. If True, the procedure will also
                        detect and assign weights to inverse relations of Allen's algebra.
        :return: None (modifies self._burst_matrix in place)
        """

        # reset the two final dataframes
        self._initialize_dataframes()

        # loop over all the rows in the dataframe (i.e. over all the bursts)
        for index1, row in self._bursts.iterrows():
            word1 = row['keyword']
            start1 = int(row['start'])
            end1 = int(row['end'])

            # among all the bursts, subsect only bursts that are not 'too before' or 'too after'
            # (considering a max admissible gap)
            # subsection = bursts.loc[(bursts['start']<(end1+max_gap)) & (bursts['end']>(start1-max_gap))]

            # consider only the bursts of words different from the current word
            subsection = self._bursts.where(self._bursts['keyword'] != word1).dropna()

            # loop over all the candidate bursts
            for index2, row2 in subsection.iterrows():

                word2 = row2['keyword']
                start2 = int(row2['start'])
                end2 = int(row2['end'])

                # compute the specific tolerance gap
                tol_gap = self._prop_tol_gap(start1, end1, start2, end2, alpha)

                # check if there is a relationship and assign the weight

                ### direct relations

                # equals
                if self._equals(start1, end1, start2, end2, tol_gap):
                    self._store_weight('equals', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # finishes
                if self._finishes(start1, end1, start2, end2, tol_gap):
                    self._store_weight('finishes', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # starts
                if self._starts(start1, end1, start2, end2, tol_gap):
                    self._store_weight('starts', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # includes
                if self._includes(start1, end1, start2, end2, tol_gap):
                    self._store_weight('includes', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # meets
                if self._meets(start1, end1, start2, end2, tol_gap):
                    self._store_weight('meets', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # overlaps
                if self._overlaps(start1, end1, start2, end2, tol_gap):
                    self._store_weight('overlaps', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                # before
                if self._before(end1, start2, tol_gap, max_gap):
                    self._store_weight('before', word1, word2, start1, end1,
                                       start2, end2, index1, index2)

                ### inverse relations

                if find_also_inverse:

                    # met-by
                    if self._met_by(start1, start2, end2, tol_gap):
                        self._store_weight('met-by', word1, word2, start1, end1,
                                           start2, end2, index1, index2)

                    # overlapped-by
                    if self._overlapped_by(start1, end1, start2, end2, tol_gap):
                        self._store_weight('overlapped-by', word1, word2, start1, end1,
                                           start2, end2, index1, index2)

                    # during
                    if self._during(start1, end1, start2, end2, tol_gap):
                        self._store_weight('during', word1, word2, start1, end1,
                                           start2, end2, index1, index2)

                    # started-by
                    if self._started_by(start1, end1, start2, end2, tol_gap):
                        self._store_weight('started-by', word1, word2, start1, end1,
                                           start2, end2, index1, index2)

                    # finished-by
                    if self._finished_by(start1, end1, start2, end2, tol_gap):
                        self._store_weight('finished-by', word1, word2, start1, end1,
                                           start2, end2, index1, index2)

                    # after
                    if self._after(start1, end2, tol_gap, max_gap):
                        self._store_weight('after', word1, word2, start1, end1,
                                           start2, end2, index1, index2)


    # HELPER METHODS FOR detect_relations: _prop_tol_gap; _store_weight

    def _prop_tol_gap(self, start1, end1, start2, end2, alpha=0.05) -> float:
        """Returns a gap that is proportional to the lengths of two bursts

        alpha (float): proportionality coefficient (it will be multiplied by the
                        total length of the two bursts).

        """

        # add 1 because the last sentence is included in the burst
        length1 = (end1 - start1) + 1
        length2 = (end2 - start2) + 1

        # compute the specific tol_gap for these two bursts
        tol_gap = (length1 + length2) * alpha

        return tol_gap

    def _store_weight(self, relation: str, word1: str, word2: str, start1: int, end1: int,
                      start2: int, end2: int, index1: int, index2: int):
        """"""

        # append the relationship at the end of the dataframe of burst pairs
        idx = self._burst_pairs.shape[0]
        self._burst_pairs.loc[idx] = [word1, word2,
                                      index1, index2,
                                      start1, end1, start2, end2, relation]

        # keep the weight in the final data structure only if it's greater than the currently stored weight
        if self._relations_weights[relation] > self._burst_matrix.at[index1, index2]:
            # add weight in the matrix
            self._burst_matrix.at[index1, index2] = self._relations_weights[relation]

    # HELPER METHODS FOR DEFINING RULES

    def _equals(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((abs(start1 - start2) < tol_gap) &
                (abs(end1 - end2) < tol_gap))

    def _finishes(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((abs(start1 - start2) > tol_gap) &
                (abs(end1 - end2) < tol_gap) &
                (start1 > start2) &
                (start1 < end2))

    def _starts(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((abs(start1 - start2) < tol_gap) &
                (abs(end1 - end2) > tol_gap) &
                (end1 > start2) & (end1 < end2))

    def _during(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 > start2) &
                (end1 < end2) &
                (abs(start1 - start2) > tol_gap) &
                (abs(end1 - end2) > tol_gap))

    def _meets(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 < start2) &
                (end1 < end2) &
                (abs(end1 - start2) < tol_gap))

    def _overlaps(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 < start2) &
                (end1 > start2) &
                (abs(end1 - start2) > tol_gap) &
                (end1 < end2) &
                (abs(end2 - end1) > tol_gap) &
                (abs(start2 - start1) > tol_gap))

    def _before(self, end1, start2, tol_gap, max_gap) -> bool:
        """"""
        return ((start2 > (end1 + tol_gap)) &
                ((start2 - end1) <= max_gap))

    def _met_by(self, start1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 > start2) &
                (start1 > end2) &  # FIXME: anche se le inverse non sono state quasi mai usate, provare ad eliminare questa regola (non si verifica in alcuni casi)
                (abs(start1 - end2) < tol_gap))

    def _overlapped_by(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 > start2) &
                (start1 < end2) &
                (abs(start1 - end2) > tol_gap) &
                (abs(start1 - start2) > tol_gap) &
                (end1 > end2) &
                (abs(end1 - end2) > tol_gap))

    def _includes(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 < start2) &
                (end1 > end2) &
                (abs(start1 - start2) > tol_gap) &
                (abs(end1 - end2) > tol_gap))

    def _started_by(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((end1 > end2) &
                (start1 < end2) &
                (abs(start1 - start2) < tol_gap) &
                (abs(end1 - end2) > tol_gap))

    def _finished_by(self, start1, end1, start2, end2, tol_gap) -> bool:
        """"""
        return ((start1 < start2) &
                (end1 > start2) &
                (abs(start1 - start2) > tol_gap) &
                (abs(end1 - end2) < tol_gap))

    def _after(self, start1, end2, tol_gap, max_gap) -> bool:
        """"""
        return ((start1 > (end2 + tol_gap)) &
                ((start1 - end2) <= max_gap))

    @property
    def bursts(self):
        """Getter of the input dataframe containing the bursts."""
        return self._bursts

    @property
    def relations_weights(self):
        """Getter of the dictionary containing the weights for all relations in Allen's algebra"""
        return self._relations_weights

    @property
    def bursts_weights(self):
        """Getter of the final dataframe containing the weights between all bursts."""
        return self._burst_matrix

    @property
    def burst_pairs(self):
        """Getter of the final dataframe containing pairs of related bursts in the format needed for machine learning project."""
        return self._burst_pairs

    def __repr__(self):
        return "WeightAssigner(bursts={}, relations_weights={})".format(
            repr(self._bursts), repr(self._relations_weights))

    def __str__(self):
        return "WeightAssigner object. Input bursts (only first 5 rows):\n{}\n,\nrelations_weights:{}".format(
            repr(self._bursts.head()), repr(self._relations_weights))

