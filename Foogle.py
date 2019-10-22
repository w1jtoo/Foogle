from App.AppContainer import AppContainer
from App.Terminal.Teminal import Terminal
from App.Config import Config
import argparse
import sys
import os.path
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Common.DateBase.BaseProvider import BaseProvider
from chardet import UniversalDetector
import sqlite3
from App.Common.utils import get_files


class Foogle:
    def __init__(self):
        self.base_provider = BaseProvider(self.get_config().get_date_base_name())

        self.parser = argparse.ArgumentParser(description="Foogle")

        # TODO Subparser compile and query and add_parser
        # self.terminal = Terminal(self.container)

    def init_container(self):
        pass

    def get_config(self) -> Config:
        return Config()

    def compile(self, directory: str) -> None:
        print("Start of reverce index building...")

        self._index = ReverceIndexBuilder(
            get_files(directory), self.base_provider
        )
        self.base_provider.recompile()

        self.fill_in_encoding_base(directory)
        self._index.compile()

        print("Base was compiled successfully")

    def fill_in_encoding_base(self, directory: str) -> None:
        for path in get_files(directory):
            self._index.base_provider.add_encoding_file(
                path, self.detect_encoding(path)
            )

    def query(self, query: str, directory: str) -> None:

        if not os.path.exists(directory):
            self.parser.error("Can't find the directory")

        print("Loading answer...")
        self._index = ReverceIndexBuilder(
            get_files(directory), self.base_provider
        )
        if not self._index:
            self.parser.error("You should compile index first.")

        print("Result files:\n" + "\n".join(self._index.get_static_query(query)))

    def detect_encoding(self, file_name: str) -> str:
        u = UniversalDetector()
        encoding = "NULL"
        with open(file_name, "rb") as f:
            for line in f.readlines():
                u.feed(line)
        u.close()
        if u.result["encoding"]:
            encoding = u.result["encoding"]
        else:
            print(f"Can't detect file encoding - '{file_name}'")
        return encoding


if __name__ == "__main__":
    # TODO replace sqlite queries to static class, less coherence
    
    parser = argparse.ArgumentParser(
        description="Pretends to be git", usage="Foogle --query [<dir>]"
    )

    parser.add_argument(
        "--query", metavar="param", help="find query in a datebase", nargs=2
    )

    parser.add_argument(
        "--compile", metavar="param", help="compile new datebase", nargs=1
    )

    args = parser.parse_args()
    foogle = Foogle()

    if args.compile:
        foogle.compile(args.compile[0])
    elif args.query:
        foogle.query(args.query[0], args.query[1])
