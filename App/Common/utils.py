import os
import time
from mimetypes import guess_type, types_map
from typing import List


def get_files(path_name: str) -> List[str]:
    result: List[str] = []
    for dirpath, _, files in os.walk(path_name):
        for file_name in files:
            result.append(os.path.abspath(os.path.join(dirpath, file_name)))
    return result


def filter_files(files: list, types: list, extention_types=[]) -> List[str]:
    result: List[str] = []
    _types = []

    for _type in extention_types:
        if _type in types_map:
            _types.append(types_map[_type])
        else:
            print(f"Can't recognize what type is '{_type}'")

    for _file in files:
        guessed = guess_type(_file)[0]
        if guessed in _types or guessed in types:
            result.append(os.path.abspath(_file))

    return result
