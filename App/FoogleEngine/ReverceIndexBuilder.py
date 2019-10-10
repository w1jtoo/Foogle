import os
import re
import math
import sqlite3
from chardet import UniversalDetector
from App.Common.DateBase.BaseProvaider import BaseProvider


CLEANING_PATTERN = re.compile(r"[\W_]+")
INDEX_BASE_NAME = "index_base"
STATE_BASE_NAME = "state_base"
IDF_BASE_NAME = "idf_base"


class ReverceIndexBuilder:
    def __init__(self, files: list, base_file_name: str):

        # INIALIZE TOTAL DATEBASE
        #   | word | path | position |

        cur = self._connection.cursor()
        cur.execute("DROP TABLE " + INDEX_BASE_NAME)
        cur.execute(
            "create table if not exists "
            + INDEX_BASE_NAME
            + " (word text, path text, position real)"
        )

        # INIALIZE TOTAL DATEBASE
        #   | pth | word | tf |

        cur = self._connection.cursor()
        cur.execute("DROP TABLE IF EXISTS " + STATE_BASE_NAME)
        cur.execute(
            "CREATE TABLE " + STATE_BASE_NAME + " (path text, word text, tf real)"
        )

        # INIALIZE TOTAL DATEBASE
        #   | term | idf |

        cur = self._connection.cursor()
        cur.execute("DROP TABLE IF EXISTS " + IDF_BASE_NAME)
        cur.execute("CREATE TABLE " + IDF_BASE_NAME + " (term text, idf real)")

        self.files = files
        # self.tf = {}
        # self.df = {}
        # self.idf = {}
        # self.magnitudes = {}
        # self.vectors = {}

    def set_directory(self, connection):
        self._connection = connection

    def idf_func(self, N, N_t):
        return math.log(N / N_t) if N_t != 0 else 0


    def compile(self):
        self._builder_init()

        self._inialize_stats()

    def _builder_init(self):
        # there is some optimization
        # so we can do it in 2o(nl) instead of 3o(nl)
        c = self._connection.cursor()

        for fname in self.files:
            position = 0
            f = open(fname, "r")
            while 1:
                line = f.readline().lower()
                if not line:
                    break
                for word in line.split(" "):
                    c.execute(
                        "INSERT INTO {} VALUES ('{}','{}',{})".format(
                            INDEX_BASE_NAME, word, fname, position
                        )
                    )
                    position += len(word)
                position += len(line)
            f.close()
        self._connection.commit()

    def get_terms(self) -> list:
        """ Should return pair of word and path"""
        # TODO
        c = self._connection.cursor()
        c.execute("SELECT DISTINCT word, path FROM {}".format(INDEX_BASE_NAME))
        terms = c.fetchall()

        return terms

    def set_term_frequency(self, terms=[]) -> None:
        # CAN BE OPTIMIZED
        if not terms:
            terms = self.get_terms()

        cursor = self._connection.cursor()

        for term, path in terms:

            # GET FROM TABLE
            cursor.execute(
                "SELECT COUNT(*) FROM {} \
                 WHERE word = '{}' AND path = '{}'".format(
                    INDEX_BASE_NAME, term, path
                )
            )
            count_of_term = cursor.fetchall()[0][0]

            cursor.execute(
                "SELECT COUNT(*) FROM {} \
                 WHERE path = '{}'".format(
                    INDEX_BASE_NAME, path
                )
            )
            total_term_count = cursor.fetchall()[0][0]

            # WRITE TABLE
            # TODO write this to main date base couse of nothing
            # special in this terms to write it to single date base
            # tf(t, doc) = A / B where
            # a:= count of t in doc
            # b:= total count of word in doc
            cursor.execute(
                "INSERT INTO {} VALUES ('{}', '{}', {})".format(
                    STATE_BASE_NAME, path, term, count_of_term / total_term_count
                )
            )

        self._connection.commit()

    def get_paths_what_word_in(self, word: str) -> list:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT DISTINCT path  FROM {} \
                 WHERE word = '{}'".format(
                INDEX_BASE_NAME, word
            )
        )
        return [path[0] for path in cursor.fetchall()]

    def set_inverce_frequency(self) -> None:
        # CAN BE OPTIMIZED
        cursor = self._connection.cursor()

        # get unique term list
        cursor.execute("SELECT DISTINCT word FROM {}".format(INDEX_BASE_NAME))
        terms = [term[0] for term in cursor.fetchall()]

        for term in terms:
            cursor.execute(
                "SELECT COUNT (DISTINCT path) FROM {} \
                 WHERE word = '{}' ".format(
                    INDEX_BASE_NAME, term
                )
            )
            document_count = cursor.fetchone()[0]

            # idf(term) = log( len(files) / count of docs with term )
            cursor.execute(
                "INSERT INTO {} VALUES ('{}', {})".format(
                    IDF_BASE_NAME, term, math.log(len(self.files) / document_count)
                )
            )
        self._connection.commit()

    def get_positions_in_file(self, word: str, path: str) -> list:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT position FROM {} \
                 WHERE word = '{}' AND path = '{}' ".format(
                INDEX_BASE_NAME, word, path
            )
        )
        return [path[0] for path in cursor.fetchall()]

    def _inialize_stats(self):
        termins = self.get_terms()
        self.set_inverce_frequency()
        self.set_term_frequency(terms=termins)

    def get_static_query(self, string: str) -> list:
        string = string.lower()
        pattern = re.compile(r"[\W_]+")
        string = pattern.sub(" ", string)
        lists, result = [], []

        cursor = self._connection.cursor()
        cursor.execute("SELECT DISTINCT word FROM {}".format(INDEX_BASE_NAME))
        terms = [term[0] for term in cursor.fetchall()]

        for word in string.split():
            # make query for a single word
            if word in terms:
                # add rank
                lists.append([*self.get_paths_what_word_in(word)])
            else:
                lists.append([])

        # CAN BE FASTER
        setted = set(lists[0]).intersection(*lists)

        for filename in setted:
            temp_list = []
            for word in string.split():
                # TODO HERE!!!
                temp_list.append(self.get_positions_in_file(word, filename))
            for i in range(len(temp_list)):
                for ind in range(len(temp_list[i])):
                    temp_list[i][ind] -= i
            if set(temp_list[0]).intersection(*temp_list):
                result.append(filename)
        return self._get_rank(result, string)

    def _term_total_freq(self, terms, query):
        temp = [0] * len(terms)
        for i, term in enumerate(terms):
            count = 0
            for word in query.split():
                if word == term:
                    count += 1
            temp[i] = count
        return temp

    def get_term_frequency(self, fname: str, term: str) -> int:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT tf FROM {} \
                 WHERE word = '{}' AND path = '{}' ".format(
                STATE_BASE_NAME, term, fname
            )
        )
        result = cursor.fetchone()
        if result is None:
            return 0
        return result[0]

    def get_inverce_term_frequency(self, term: str) -> int:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT idf FROM {} \
                 WHERE term = '{}' ".format(
                IDF_BASE_NAME, term
            )
        )
        return cursor.fetchone()[0]

    def _make_vectors_for_query(self, fnames: str, terms=[]) -> dict:

        cursor = self._connection.cursor()
        cursor.execute("SELECT DISTINCT word FROM {}".format(INDEX_BASE_NAME))
        terms = [term[0] for term in cursor.fetchall()]

        vecs = {}
        for f in fnames:
            vdoc = [0] * len(terms)
            for ind, term in enumerate(terms):
                print(str(ind) + term)
                vdoc[ind] = self.get_term_frequency(
                    f, term
                ) * self.get_inverce_term_frequency(term)
            vecs[f] = vdoc
        return vecs

    def _query_vecor(self, query: str, terms=[]) -> list:
        cursor = self._connection.cursor()
        cursor.execute("SELECT DISTINCT word FROM {}".format(INDEX_BASE_NAME))
        terms = [term[0] for term in cursor.fetchall()]

        pattern = re.compile(r"[\W_]+")
        query = pattern.sub(" ", query)
        queryls = query.split()
        vquery = [0] * len(queryls)
        index = 0
        for _, word in enumerate(queryls):
            vquery[index] = self.queryFreq(word, query)
            index += 1
        queryidf = [self.get_inverce_term_frequency(word) for word in terms]
        magnitude = pow(sum(map(lambda x: x ** 2, vquery)), 0.5)
        freq = self._term_total_freq(terms, query)
        tf = [x / magnitude for x in freq]
        final = [tf[i] * queryidf[i] for i in range(len(terms))]
        return final

    def queryFreq(self, term, query):
        count = 0
        for word in query.split():
            if word == term:
                count += 1
        return count

    def _product(self, doc1, doc2):
        if len(doc1) != len(doc2):
            return 0
        return sum([x * y for x, y in zip(doc1, doc2)])

    def _get_rank(self, result_files, query) -> list:
        vectors = self._make_vectors_for_query(result_files)
        queryVec = self._query_vecor(query)
        results = [
            [self._product(vectors[result], queryVec), result]
            for result in result_files
        ]
        results.sort(key=lambda x: x[0])
        results = [x[1] for x in results]
        return results
