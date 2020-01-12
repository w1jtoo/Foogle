from os import path
from pathlib import Path
import yaml
from typing import Dict, Any, List, Optional


class Config:
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
                cls.__instance.config = entries.get("foogle")
        return cls.__instance

    def get_general_path(self) -> str:
        return path.abspath(path.join(str(Path.home()) + "/.foogle"))

    def __getattr__(self, name):
        return self.config.get(name) or Config.__standart_entries.get(name)

    def is_standart(self, attribute: str) -> bool:
        if self.config.get(attribute) is None:
            return True
        return self.config.get(attribute) == Config.__standart_entries.get(attribute)

    def get_all_names(self) -> List[str]:
        return self.__standart_entries.keys()

    def get_value(self, key: str) -> Any:
        return self.config.get(key) or Config.__standart_entries.get(key)
