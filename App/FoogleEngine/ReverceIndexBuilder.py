import os
import re
import math
import sqlite3
from chardet import UniversalDetector
from App.Common.DateBase.BaseProvider import BaseProvider, DateBase


CLEANING_PATTERN = re.compile(r"[\W_]+")


class ReverceIndexBuilder:
    def __init__(self, files: list, base_provider: BaseProvider):
        self.base_provider = base_provider
        self.files = files

    def compile(self):
        self._builder_init()

        self._inialize_stats()

    def _builder_init(self):
        # there is some optimization
        # so we can do it in 2o(nl) instead of 3o(nl)

        for fname in self.files:
            position = 0
            encoding = self.base_provider.get_encoding(fname)
            if encoding == "NULL":
                print(f"Can't load file encoding: '{fname}'")
                continue

            f = open(fname, "r", encoding=encoding)
            while 1:
                line = f.readline().lower()
                if not line:
                    break
                for word in line.split(" "):
                    self.base_provider.insert_into(
                        DateBase.INDEX, word, fname, position
                    )
                    position += len(word)
                position += len(line)
            f.close()

    def set_term_frequency(self, terms=[]) -> None:
        if not terms:
            terms = self.base_provider.get_terms_and_paths()

        for term, path in terms:
            count_of_term = self.base_provider.select_count(
                DateBase.INDEX, where=f"path = '{path}' AND word= '{term}'"
            )

            total_term_count = self.base_provider.select_count(
                DateBase.INDEX, where=f"path = '{path}'"
            )

            # WRITE TABLE
            # TODO write this to main date base couse of nothing
            # special in this terms to write it to single date base
            # tf(t, doc) = A / B where
            # a:= count of t in doc
            # b:= total count of word in doc

            self.base_provider.insert_into(
                DateBase.TF, path, term, count_of_term / total_term_count
            )

    def set_inverce_frequency(self) -> None:
        # CAN BE OPTIMIZED

        # get unique term list

        terms = [
            term[0]
            for term in self.base_provider.select_distinct(
                DateBase.INDEX, distinct_params="word"
            )
        ]

        for term in terms:
            document_count = self.base_provider.select_count(
                DateBase.INDEX,
                count_params="DISTINCT path",
                where=f"word = '{term}'",
            )

            self.base_provider.insert_into(
                DateBase.IDF, term, math.log(len(self.files) / document_count)
            )

    def get_positions_in_file(self, word: str, path: str) -> list:

        positions = self.base_provider.select_all(
            DateBase.INDEX,
            select_params="position",
            where=f" word = '{word}' AND path = '{path}' ",
        )
        return [path[0] for path in positions]

    def _inialize_stats(self):
        termins = self.base_provider.get_terms_and_paths()
        self.set_inverce_frequency()
        self.set_term_frequency(terms=termins)

    def get_static_query(self, string: str) -> list:
        string = string.lower()
        pattern = re.compile(r"[\W_]+")
        string = pattern.sub(" ", string)
        lists, result = [], []

        terms = [
            term[0]
            for term in self.base_provider.select_distinct(
                DateBase.INDEX, distinct_params="word"
            )
        ]

        for word in string.split():
            # make query for a single word
            if word in terms:
                # add rank
                paths = self.base_provider.select_distinct(
                    DateBase.INDEX, where=f"word = '{word}'", distinct_params="path"
                )

                lists.append([*[path[0] for path in paths]])
            else:
                lists.append([])

        # CAN BE FASTER
        setted = set(lists[0]).intersection(*lists)
        for filename in setted:
            temp_list = []
            for word in string.split():
                # TODO HERE!!!
                t = self.base_provider.select_all(
                    DateBase.INDEX,
                    where=f"word = '{word}' AND path = '{filename}'",
                    select_params="position",
                )

                temp_list.append([w[0] / len(word) for w in t])
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
        # cursor.execute(
        #     "SELECT tf FROM {} \
        #          WHERE word = '{}' AND path = '{}' ".format(
        #         STATE_BASE_NAME, term, fname
        #     )
        # )
        result = self.base_provider.select_one(
            DateBase.TF,
            where=f"word = '{term}' AND path = '{fname}'",
            select_params="tf",
        )
        if not result:
            return 0
        return result[0]

    def get_inverce_term_frequency(self, term: str) -> int:
        result = self.base_provider.select_one(
            DateBase.IDF, where=f" term = '{term}' ", select_params="idf"
        )
        if result[0]:
            return 0
        return result[0][0]

    def terms(self) -> list:
        result = self.base_provider.select_distinct(
            DateBase.INDEX, distinct_params="word"
        )

        return [term[0] for term in result]

    def _make_vectors_for_query(self, fnames: str, terms=[]) -> dict:

        # cursor.execute("SELECT DISTINCT word FROM {}".format(INDEX_BASE_NAME))

        vecs = {}
        for f in fnames:
            vdoc = [0] * len(terms)
            for ind, term in enumerate(terms):
                vdoc[ind] = self.get_term_frequency(
                    f, term
                ) * self.get_inverce_term_frequency(term)
            vecs[f] = vdoc
        return vecs

    def _query_vecor(self, query: str, terms=[]) -> list:

        pattern = re.compile(r"[\W_]+")
        query = pattern.sub(" ", query)
        queryls = query.split()
        vquery = [0] * len(queryls)
        index = 0
        for _, word in enumerate(queryls):
            vquery[index] = self._get_query_frequency(word, query)
            index += 1
        queryidf = [self.get_inverce_term_frequency(word) for word in terms]
        magnitude = pow(sum(map(lambda x: x ** 2, vquery)), 0.5)
        freq = self._term_total_freq(terms, query)
        tf = [x / magnitude for x in freq]
        final = [tf[i] * queryidf[i] for i in range(len(terms))]
        return final

    def _get_query_frequency(self, term, query):
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

        terms = self.terms()
        vectors = self._make_vectors_for_query(result_files, terms=terms)
        queryVec = self._query_vecor(query, terms=terms)
        results = [
            [self._product(vectors[result], queryVec), result]
            for result in result_files
        ]
        results.sort(key=lambda x: x[0])
        results = [x[1] for x in results]
        return results
