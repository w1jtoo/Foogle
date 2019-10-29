from pathlib import Path
from os import path


class Config:
    # TODO Connect serialization using Yaml
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def get_date_base_name(self) -> str:
        return "foogledatebase.db"

    def update(self):
        pass

    def get_types(self) -> list:
        return ["text/plain"]

    def get_types_extention(self) -> list:
        return []

    def get_general_path(self) -> str:
        return path.abspath(str(Path.home()) + "\\.foogle")
