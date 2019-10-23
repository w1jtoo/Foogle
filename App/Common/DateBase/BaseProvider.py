# TODO replace it to cnfg file


import sqlite3
import enum

# will work after python 3.9
# see https://docs.pytest.org/en/latest/warnings.html
from collections.abc import Iterator

from App.Common.DateBase.SelectError import SelectError

# TODO make linq
class DateBase(enum.Enum):
    INDEX = 1
    TF = 2
    IDF = 3
    ENCODING = 4
    SQLITE_MASTER = 5 

    def __str__(self):
        if self is DateBase.SQLITE_MASTER:
            return str(self.name).lower()
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
             ( word TEXT, path TEXT, position REAL, utf_id INTEGER, uidf_id INTEGER ) "
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

    def get_terms_paths_iterator(self) -> Iterator:
        """ Returns iterator that iterable by pair of word and path"""
        return TermsPathsItermator(self)

    def get_terms_cpunt(self) -> int:
        return len(TermsPathsItermator(self))

    def get_terms_iterator(self) -> Iterator:
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

    def is_valid(self) -> bool:
        """Return if DateBase ready to work.
        Returns
        -------
        bool 
            True if tables inialized else False.
        """
        index = self.select_one(
            DateBase.SQLITE_MASTER,
            select_params="name",
            where=f"type = 'table' AND name= '{DateBase.INDEX}'",
        )
        if index:
            index = index[0] == str(DateBase.INDEX)
        else:
            return False
        tf = self.select_one(
            DateBase.SQLITE_MASTER,
            select_params="name",
            where=f"type = 'table' AND name= '{DateBase.TF}'",

        ) 
        if tf:
            tf = tf[0] == str(DateBase.TF)
        else:
            return False
        idf = self.select_one(
            DateBase.SQLITE_MASTER,
            select_params="name",
            where=f"type = 'table' AND name= '{DateBase.IDF}'"

        )
        if idf:
            idf = idf[0] == str(DateBase.IDF)
        else:
            return False
        encode = self.select_one(
            DateBase.SQLITE_MASTER,
            select_params="name",
            where=f"type = 'table' AND name= '{DateBase.ENCODING}'" ,

        )
        if encode:
            encoding = encode[0] == str(DateBase.ENCODING)
        else:
            return False

        return encode and idf and tf and index

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
        """
        encoding = self.select_one(
            DateBase.ENCODING,
            where=f"path = '{file_name}'",
            select_params="encoding",
        )
        if not encoding:
            return "UTF-8"
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

    def recompile(self) -> None:
        """Drop existing tables and creates new ones. """
        self.drop_tables()
        self.initalize_file_encoding()
        self.initalize_idf_base()
        self.initalize_tf_base()
        self.initialize_index_base()


class TermsPathsItermator:
    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def __iter__(self):
        self._counter = 1
        return self

    def __next__(self):
        result = self._provider.select_one(
            DateBase.INDEX,
            where=f"utf_id={self._counter}",
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
        return self._provider.select_count(DateBase.INDEX)

    def __next__(self):
        result = self._provider.select_one(
            DateBase.INDEX, where=f"uidf_id={self._counter}", select_params="word"
        )

        if result:
            self._counter += 1
            return result[0]
        else:
            raise StopIteration
