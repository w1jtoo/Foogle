import sqlite3
import os

class DateBaseEntity:
    """Creates temp date base. """

    def __init__(self, base_name: str):
        self.base_name = base_name

    def __enter__(self):
        base = open(self.base_name, "w+")
        base.close()

    def __exit__(self, type, value, tb):
        os.remove(os.path.join(self.base_name))
