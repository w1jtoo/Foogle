from os import path
from pathlib import Path
import yaml
from typing import Dict, Any


class Config:
    # TODO Connect serialization using Yaml
    __instance = None
    file_name = "foogle_config.yaml"
    __standart_entries: Dict[str, Any] = {
        "types": ["text*"],
        "date_base_name": "foogledatebase.db",
        "logging_file_name": "FoogleLog.log",
        "extention_types": [],
        "general_path": (path.join(str(Path.home()), ".foogle")),
    }

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
            with open(cls.file_name, "r") as f:
                entries = yaml.safe_load(f)
                # print(entries)
                cls.__instance.cofig = entries.get("foogle")
        return cls.__instance

    def get_general_path(self) -> str:
        return path.abspath(path.join(str(Path.home()) + "/.foogle"))

    def __getattr__(self, name):
        return self.cofig.get(name) or Config.__standart_entries.get(name)
