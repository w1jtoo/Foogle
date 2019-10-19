# TODO replace it to cnfg file


import sqlite3
import enum

from App.Common.DateBase.SelectError import SelectError

# TODO make linq
class DateBase(enum.Enum):
    INDEX = 1
    TF = 2
    IDF = 3
    ENCODING = 4

    def __str__(self):
        return str(self.name).lower() + "_base"


class BaseProvider:
    # TODO I should use Date Base normalization but nowdays it's to time expensive for me
    def __init__(self, db_name: str):
        """"""
        self._db_name = db_name
        self._connection = sqlite3.connect(self._db_name)
        self._cursor = self._connection.cursor()

    def drop_table(self, base: DateBase) -> None:
        """Drop table only if it exists."""
        self._cursor.execute(f"DROP TABLE IF EXISTS {base} ")

    def initialize_index_base(self) -> None:
        """
        Initialize dase where word, path, position and id of word entry.
        
        View: 
        | word | path | position | id |
        """
        self._cursor.execute(
            f" CREATE TABLE {DateBase.INDEX} \
             ( word TEXT, path TEXT, position REAL, id INTEGER ) "
        )
        self._connection.commit()

    def initalize_tf_base(self) -> None:
        """ Initialize dase word, path and it's tf.  

        View:
        | path | word | tf | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.TF} ( path text, word text, tf real )"
        )
        self._connection.commit()

    def initalize_idf_base(self) -> None:
        """ Initialize dase word, path and it's tf.

        View:
        | id | term | idf | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.IDF} (id INTEGER PRIMARY KEY AUTOINCREMENT, term text, idf real)"
        )
        self._connection.commit()

    def initalize_file_encoding(self) -> None:
        """ Initialize base with file and it's encoding.

        View:
        | id | path | encoding | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.ENCODING} ( ID INTEGER PRIMARY KEY AUTOINCREMENT, path text, encoding text )"
        )
        self._connection.commit()

    def add_encoding_file(self, path: str, encoding: str) -> None:
        self._cursor.execute(
            f"INSERT INTO {DateBase.ENCODING} (path, encoding) VALUES ( '{path}', '{encoding}')"
        )
        self._connection.commit()

    def get_terms_paths_iterator(self) -> iter:
        """ Returns iterator that iterable by pair of word and path"""
        return TermsPathsItermator(self)

    def get_terms_iterator(self) -> iter:
        """ Returns iterator that iterable by words."""
        return TermsItermator(self)

    def select_count(self, base: DateBase, where="", count_params="*") -> int:
        """ Select count of something in DateBase. Equivalent of SQL's SELECT COUNT...

        Parameters
        ----------
        base : DateBase
            type of DateBase.
        where : str
            condition that used to count item. Equivalent of SQL's WHERE
        count_params : str
            what sql's entity like tables, columns etc. should be returned. 
        Returns
        -------
        int
            Count of applicable items. 

        """
        query = f"SELECT COUNT({count_params}) FROM {base}"
        if where:
            query += f" WHERE {where}"
        self._cursor.execute(query)
        result = self._cursor.fetchone()

        return result[0]

    def select_all(self, base: DateBase, where="", select_params="*") -> list:
        """ Select all tuples of something in DateBase. Equivalent of SQL's SELECT...

        Parameters
        ----------
        base : DateBase
            type of DateBase.
        where : str
            condition that used to count item. Equivalent of SQL's WHERE
        select_params : str
            what sql's entity like tables, columns etc. should be returned. 
        Returns
        -------
        list
            list of tuples that mapped in base. 
            
        """
        if select_params == "*":
            query = f"SELECT * FROM {base}"
        else:
            query = f"SELECT ({select_params}) FROM {base}"
        if where:
            query += f" WHERE {where}"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def select_one(self, base: DateBase, where="", select_params="*") -> tuple:
        """ Select tuple of something in DateBase. Equivalent of SQL's SELECT...

        Parameters
        ----------
        base : DateBase
            type of DateBase.
        where : str
            condition that used to count item. Equivalent of SQL's WHERE
        select_params : str
            what sql's entity like tables, columns etc. should be returned. 
        Returns
        -------
        tuple
            what was mapped in base. 
            
        """
        if select_params == "*":
            query = f"SELECT * FROM {base}"
        else:
            query = f"SELECT {select_params} FROM {base}"

        if where:
            query += f" WHERE {where}"
        # print(query)
        self._cursor.execute(query)
        return self._cursor.fetchone()

    def insert_into(self, base: DateBase, *values) -> None:
        """ Insert into table values.

        Parameters
        ----------
        base : DateBase
            type of DateBase.
        *values : str, int, float
            values that should be inserted. 
        """
        # make str values to it's format
        result = []
        for value in values:
            if isinstance(value, str):
                result.append(f"'{value}'")
            elif str(value).replace(".", "", 1).isdigit():
                result.append(str(value))

        if base == DateBase.IDF:
            self._cursor.execute(
                f"INSERT INTO {base} (term, idf) VALUES ({', '.join(result)})"
            )
            self._connection.commit()
            return
        self._cursor.execute(f"INSERT INTO {base} VALUES ({', '.join(result)})")
        self._connection.commit()

    def select_distinct(
        self, date_base: DateBase, where="", distinct_params="*"
    ) -> list:
        """ Select unique tuples of something in DateBase. Equivalent of SQL's SELECT DISTINCT...

        Parameters
        ----------
        base : DateBase
            type of DateBase.
        where : str
            condition that used to count item. Equivalent of SQL's WHERE
        distinct_params : str
            what sql's entity like tables, columns etc. should be returned. 
        Returns
        -------
        list
            list of tuples that mapped in base. 
            
        """

        query = f"SELECT DISTINCT {distinct_params} FROM {date_base}"
        if where:
            query += f" WHERE {where}"
        self._cursor.execute(query)

        return self._cursor.fetchall()

    def get_encoding(self, file_name: str) -> str:
        """Return encoding of file
        Raises
        ------
        SelectError
            If can't find file's encoding in Encoding date base.
        
        """
        encoding = self.select_one(
            DateBase.ENCODING,
            where=f"path = '{file_name}'",
            select_params="encoding",
        )
        if not encoding:
            raise SelectError
        return encoding[0]

    def __enter__(self):
        # TODO create good solution of this problem
        return self

    def __exit__(self, type, value, tb):
        self._connection.close()

    def drop_tables(self) -> None:
        """Drop index, idf, tf and encoding table."""
        self.drop_table(DateBase.ENCODING)
        self.drop_table(DateBase.IDF)
        self.drop_table(DateBase.TF)
        self.drop_table(DateBase.INDEX)


class TermsPathsItermator:
    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        result = self._provider.select_one(
            DateBase.INDEX,
            where=f"id={self._counter}",
            select_params=" word, path ",
        )
        if result:
            self._counter += 1
            return result
        else:
            raise StopIteration


class TermsItermator:
    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def __iter__(self):
        self._counter = 1
        return self

    def __len__(self):
        return self._provider.select_count(DateBase.IDF)

    def __next__(self):
        result = self._provider.select_one(
            DateBase.IDF, where=f"id={self._counter}", select_params="term"
        )
        if result:
            self._counter += 1
            return result[0]
        else:
            raise StopIteration
