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
        Initialize dase where word, path, and position of word entry.
        
        View: 
        | word | path | position |
        """
        self._cursor.execute(
            f" CREATE TABLE {DateBase.INDEX} \
             ( word text, path text, position real ) "
        )
        self._connection.commit()

    def initalize_tf_base(self) -> None:
        """ Initialize dase word, path and it's tf.  

        View:
        | path | word | tf | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.TF} (path text, word text, tf real)"
        )
        self._connection.commit()

    def initalize_idf_base(self) -> None:
        """ Initialize dase word, path and it's tf.

        View:
        | path | word | tf | 
        """
        self._cursor.execute(f"CREATE TABLE {DateBase.IDF} ( term text, idf real )")
        self._connection.commit()

    def initalize_file_encoding(self) -> None:
        """ Initialize base with file and it's encoding.

        View:
        | id | path | encoding | 
        """
        self._cursor.execute(
            f"CREATE TABLE {DateBase.ENCODING} ( id INTEGER PRIMARY KEY AUTOINCREMENT, path text, encoding text )"
        )
        self._connection.commit()

    def add_encoding_file(self, path: str, encoding: str) -> None:
        self._cursor.execute(
            f"INSERT INTO {DateBase.ENCODING} (path, encoding) VALUES ( '{path}', '{encoding}')"
        )
        self._connection.commit()

    def get_terms_and_paths(self) -> list:
        """ Should return pair of word and path"""
        self._cursor.execute(f"SELECT DISTINCT word, path FROM {DateBase.INDEX}")
        terms = self._cursor.fetchall()

        return terms

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
            query = f"SELECT ({select_params}) FROM {base}"

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
