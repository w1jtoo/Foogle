# TODO replace it to cnfg file 

INDEX_BASE_NAME = "index_base"
STATE_BASE_NAME = "state_base"
IDF_BASE_NAME = "idf_base"

import sqlite3

class BaseProvider():
    def __init__(self, db_name: str):
        """"""
        self._connection = sqlite3.connect(db_name)

    def initialize_index_base(self):
        """"
        initialize dabe where word, path, and position of word entry
        ...
        | word | path | position |
        ...
        """
        cur = self._connection.cursor()
        cur.execute("DROP TABLE " + INDEX_BASE_NAME)
        cur.execute(
            "create table if not exists "
            + INDEX_BASE_NAME
            + " (word text, path text, position real)"
        )