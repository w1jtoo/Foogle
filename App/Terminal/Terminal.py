from tqdm import tqdm
from typing import List


class Terminal(object):
    __instance = None
    __progress_bar = None
    __broken_files: List[str] = []

    @property
    def progress_bar(self) -> tqdm:
        if not self.__progress_bar:
            raise AttributeError
        return self.__progress_bar

    def set_progress_bar(self, lenght: int) -> None:
        self.__progress_bar = tqdm(total=lenght)

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def sprint(self, string: str) -> None:
        print(string)

    def format_path(self, path: str) -> str:
        if len(path) > 30:
            return f"'...{path[-20:]}'"
        else:
            return path

    def print_state(self) -> None:
        if self.__broken_files:
            self.sprint(f"Can't detect encoding of next {len(self.__broken_files)} files : ")
            if 0 < len(self.__broken_files) < 5:
                for _file in self.__broken_files: self.sprint(f"    {_file}") 
            else:
                self.sprint("\n".join(self.__broken_files[0:5]))

    def add_broken_file(self, path: str) -> None:
        self.__broken_files.append(self.format_path(path))
