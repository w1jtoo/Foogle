# TODO replace it to cnfg file


import sqlite3
import enum

# TODO make linq
class DateBase(enum.Enum):
    INDEX = 1
    TF = 2
    IDF = 3

    def __str__(self):
        return str(self.name).lower() + "_base"


class QueryCount(enum.Enum):
    ALL = 0
    ONE = 1


class BaseProvider:
    def __init__(self, db_name: str):
        """"""
        self._connection = sqlite3.connect(db_name)
        self._cursor = self._connection.cursor()

        # drop to rewrite it
        self.drop_table(DateBase.IDF)
        self.drop_table(DateBase.INDEX)
        self.drop_table(DateBase.TF)

        # init
        self.initialize_index_base()
        self.initalize_tf_base()
        self.initalize_idf_base()

    def drop_table(self, base: DateBase) -> None:
        self._cursor.execute(f"DROP TABLE {base} ")

    def initialize_index_base(self) -> None:
        """
        Initialize dase where word, path, and position of word entry
        View:
        | word | path | position |
        """
        self._cursor.execute(
            f" CREATE TABLE {DateBase.INDEX} \
             ( word text, path text, position real ) "
        )
        self._connection.commit()

    def initalize_tf_base(self) -> None:
        """ Initialize dase word, path and it's tf  
        View:
        | path | word | tf | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.TF} (path text, word text, tf real)"
        )
        self._connection.commit()

    def initalize_idf_base(self) -> None:
        """ Initialize dase word, path and it's tf  
        View:
        | path | word | tf | 
        """
        self._cursor.execute(f"CREATE TABLE {DateBase.IDF} ( term text, idf real )")
        self._connection.commit()

    def get_terms(self) -> list:
        """ Should return pair of word and path"""
        self._cursor.execute(f"SELECT DISTINCT word, path FROM {DateBase.INDEX}")
        terms = self._cursor.fetchall()

        return terms

    def select_count(self, base: DateBase, where="", count_params="*") -> int:
        query = f"SELECT COUNT({count_params}) FROM {base}"
        if where:
            query += f" WHERE {where}"
        # print(query)
        self._cursor.execute(query)
        return self._cursor.fetchone()[0]

    def select_all(self, base: DateBase, where="", select_params="*") -> list:
        query = f"SELECT ({select_params}) FROM {base}"
        if where:
            query += f" WHERE {where}"
        # print(query)
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def select_one(self, base: DateBase, where="", select_params="*") -> tuple:
        if select_params == "*":
            query = f"SELECT {select_params} FROM {base}"
        else:
            query = f"SELECT ({select_params}) FROM {base}"

        if where:
            query += f" WHERE {where}"
        # print(query)
        self._cursor.execute(query)
        return self._cursor.fetchone()

    def insert_into(self, base: DateBase, *values) -> None:
        # make str values to it's format
        result = []
        for value in values:
            if isinstance(value, str):
                result.append(f"'{value}'")
            elif str(value).replace('.','',1).isdigit():
                result.append(str(value))
        # print(f"INSERT INTO {base} VALUES ({', '.join(result)})")
        self._cursor.execute(f"INSERT INTO {base} VALUES ({', '.join(result)})")
        self._connection.commit()

    def select_distinct(
        self, date_base: DateBase, where="", distinct_params="*"
    ) -> list:
        query = f"SELECT DISTINCT {distinct_params} FROM {date_base}"
        if where:
            query += f" WHERE {where}"
        # print(query)
        self._cursor.execute(query)

        return self._cursor.fetchall()
