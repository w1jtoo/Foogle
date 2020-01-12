import logging
import math
import os
import re
import sqlite3
from typing import List

from chardet import UniversalDetector
from logdecorator import log_exception, log_on_end, log_on_error, log_on_start

from App.Common.DateBase.BaseProvider import BaseProvider, DateBase
from App.Common.utils import detect_encoding, get_total_lenght
from App.Terminal.Terminal import Terminal

CLEANING_PATTERN = re.compile(r"[\d\w].*[\d\w]")


class ReverceIndexBuilder:
    def __init__(self, files: list, base_provider: BaseProvider):
        self.base_provider = base_provider
        self.files = files

    @log_on_error(
        logging.ERROR,
        "Error on filling up {e!r}",
        on_exceptions=Exception,
        reraise=True,
    )
    def compile(self):
        self._builder_init()
        self._inialize_stats()
        Terminal().print_state()

    @log_on_start(logging.DEBUG, "IDEX table filling up...")
    @log_on_end(logging.DEBUG, "INDEX table filled up successfully!")
    def _builder_init(self):
        # there is some optimization
        # so we can do it in 2o(nl) instead of 3o(nl)
        unique_terms_count = 1

        Terminal().set_progress_bar(get_total_lenght(self.files))

        for fname in self.files:
            path_terms_count = 1
            position = 0
            encoding = detect_encoding(fname)
            if encoding == "NULL":
                continue

            f = open(fname, "r", encoding=encoding)
            while True:
                line = f.readline().lower()
                Terminal().progress_bar.update(1)
                if not line:
                    break
                for word in re.split(r"\W+", line):
                    word = CLEANING_PATTERN.search(word)
                    if word:
                        word = word.group(0)
                    else:
                        continue

                    paths_count = self.base_provider.select_one(
                        DateBase.INDEX,
                        select_params="upt_id",
                        where=f"word=? AND path=?",
                        where_params=(word, fname),
                    )

                    word_count = self.base_provider.select_one(
                        DateBase.INDEX,
                        select_params="uterm_id",
                        where=f"word=?",
                        where_params=(word,),
                    )

                    if word_count:
                        ut_result = word_count[0]
                    else:
                        ut_result = unique_terms_count
                        unique_terms_count += 1

                    if not path_terms_count:
                        upt_result = paths_count[0]
                    else:
                        upt_result = path_terms_count
                        path_terms_count += 1

                    self.base_provider.insert_into(
                        DateBase.INDEX,
                        word,
                        fname,
                        position,
                        upt_result,
                        ut_result,
                    )
                    position += len(word)
            self.base_provider.commit()
            f.close()

        Terminal().progress_bar.close()

    def set_term_frequency(self) -> None:
        for term, path in self.base_provider.get_terms_paths_iterator():
            count_of_term = self.base_provider.select_count(
                DateBase.INDEX,
                where=f"path = ? AND word= ?",
                where_params=(path, term),
            )

            total_term_count = self.base_provider.select_count(
                DateBase.INDEX, where=f"path = ?", where_params=(path,)
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
            Terminal().progress_bar.update()
        self.base_provider.commit()

    def set_inverce_frequency(self) -> None:
        # CAN BE OPTIMIZED
        # get unique term list
        for term in self.base_provider.get_terms_iterator():
            document_count = self.base_provider.select_count(
                DateBase.INDEX,
                count_params="DISTINCT path",
                where=f"word = ?",
                where_params=(term,),
            )

            self.base_provider.insert_into(
                DateBase.IDF, term, math.log(len(self.files) / document_count)
            )
            Terminal().progress_bar.update()
        self.base_provider.commit()

    def get_positions_in_file(self, word: str, path: str) -> list:

        positions = self.base_provider.select_all(
            DateBase.INDEX,
            select_params="position",
            where=f" word =? AND path =? ",
            where_params=(word, path),
        )
        return [path[0] for path in positions]

    @log_on_start(logging.DEBUG, "TF-IDF tables filling up...")
    @log_on_end(logging.DEBUG, "TF-IDF tables filled up successfully!")
    def _inialize_stats(self):
        Terminal().sprint("Start filling in IDF-TF tables.")
        Terminal().set_progress_bar(
            self.base_provider.get_terms_and_paths_count()
            + self.base_provider.get_terms_count()
        )
        self.set_inverce_frequency()
        self.set_term_frequency()
        Terminal().progress_bar.close()

    def get_static_query(self, string: str, ranking: bool) -> list:
        string = string.lower()
        pattern = re.compile(r"[\W_]+")
        string = pattern.sub(" ", string)
        lists, result = [], []

        for word in string.split():
            # make query for a single word
            # add rank
            paths = self.base_provider.select_distinct(
                DateBase.INDEX,
                where=f"word =?",
                where_params=(word,),
                distinct_params="path",
            )
            if paths:
                lists.append([path[0] for path in paths])
            else:
                lists.append([])

        # CAN BE FASTER
        intersection = set(lists[0]).intersection(*lists) if lists else set()
        for filename in intersection:
            temp_list = []

            for word in string.split():
                # TODO HERE!!!
                t = self.base_provider.select_all(
                    DateBase.INDEX,
                    where=f"word =? AND path =?",
                    where_params=(word, filename),
                    select_params="position",
                )

                temp_list.append([w[0] / len(word) for w in t])

            for i in range(len(temp_list)):
                for ind in range(len(temp_list[i])):
                    temp_list[i][ind] -= temp_list[i][0]
            if set(temp_list[0]).intersection(*temp_list):
                result.append(filename)
        if ranking:
            return self._get_rank(result, string)
        else:
            return result

    def get_term_frequency(self, fname: str, term: str) -> int:
        # cursor.execute(
        #     "SELECT tf FROM {} \
        #          WHERE word = '{}' AND path = '{}' ".format(
        #         STATE_BASE_NAME, term, fname
        #     )
        # )
        result = self.base_provider.select_one(
            DateBase.TF,
            where=f"word =? AND path =? ",
            where_params=(term, fname),
            select_params="tf",
        )
        if not result:
            return 0
        return result[0]

    def get_inverce_term_frequency(self, term: str) -> int:
        result = self.base_provider.select_one(
            DateBase.IDF,
            where=f" term =? ",
            where_params=(term,),
            select_params="idf",
        )
        if not result:
            return 0
        return result[0]

    def _get_query_frequency(self, term: str, query: str) -> int:
        # can be faster
        count = 0
        for word in query.split():
            if word == term:
                count += 1
        return count

    def _product(self, file_name: str, query: str) -> float:

        temp_sum = 0
        for word in query.split(" "):
            temp_sum += self._get_query_frequency(word, query) ** 2

        magnitude = pow(temp_sum, 0.5)
        if not magnitude:
            magnitude = 1

        result_sum = 0.0
        for term in self.base_provider.get_terms_iterator():
            count = 0
            for word in query.split():
                if word == term:
                    count += 1

            result_sum += (
                self.get_term_frequency(file_name, term)
                * self.get_inverce_term_frequency(term) ** 2
                * (count / magnitude)
            )

        return result_sum

    def _get_rank(self, result_files, query) -> list:
        results = [
            [self._product(result, query), result] for result in result_files
        ]
        results.sort(key=lambda x: x[0], reverse=True)

        results = [x[1] for x in results]
        return results
