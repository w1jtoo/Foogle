import os
import re
import time
from mimetypes import guess_type, types_map
from typing import List

from chardet import UniversalDetector

from App.Terminal.Terminal import Terminal


def get_files(path_name: str) -> List[str]:
    result: List[str] = []
    for dirpath, _, files in os.walk(path_name):
        for file_name in files:
            result.append(os.path.abspath(os.path.join(dirpath, file_name)))
    return result


def filter_files(files: list, types: list, extention_types=[]) -> List[str]:
    result: List[str] = []
    _types = set()

    for _type in extention_types:
        if _type in types_map:
            _types.add(types_map[_type])
        else:
            Terminal().sprint(f"Can't recognize what type is '{_type}'")
    all_types = set(types) | _types
    for _file in files:
        guessed = guess_type(_file)[0]
        if guessed:
            for _type in all_types:
                if re.findall(_type, guessed):
                    result.append(os.path.abspath(_file))

    return result


def detect_encoding(file_name: str) -> str:
    u = UniversalDetector()
    encoding = "NULL"
    with open(file_name, "rb") as f:
        for line in f.readlines():
            u.feed(line)
    u.close()
    if u.result["encoding"]:
        encoding = u.result["encoding"]
    return encoding


def get_total_lenght(files: str) -> int:
    result = 0
    for fname in files:
        encoding = detect_encoding(fname)
        if encoding == "NULL":
            continue
        with open(fname, "r", encoding=encoding) as f:
            result += len(f.readlines())
    return result


import os
import platform


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
