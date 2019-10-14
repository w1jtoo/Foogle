from App.AppContainer import AppContainer
from App.Terminal.Teminal import Terminal
from App.Config import Config
import argparse
import sys
import os.path
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from chardet import UniversalDetector
import sqlite3

# TODO ASK Max how to use this fcking argparser


class Application:
    def __init__(self):
        self.container = AppContainer()
        self.parser = argparse.ArgumentParser(description="Foogle")

        # TODO Subparser compile and query and add_parser
        # self.terminal = Terminal(self.container)
        self.parser = argparse.ArgumentParser(
            description="Pretends to be git", usage="Foogle --query [<dir>]"
        )
        self.parser.add_argument(
            "--query", metavar="param", help="find query in a datebase", nargs=2
        )
        self.parser.add_argument(
            "--compile", metavar="param", help="compile new datebase", nargs=1
        )
        args = self.parser.parse_args()

        if args.compile:
            self.compile(args.compile[0])
        elif args.query:
            self.query(args.query[0], args.query[1])

    def init_container(self):
        pass

    def get_config(self) -> Config:
        return Config()

    def compile(self, directory: str) -> None:
        print("Start of reverce index building...")
        from App.Common.DateBase.BaseProvaider import DateBase
        
        
        self._index = ReverceIndexBuilder(
            self.get_files(directory), self.get_config().get_date_base_name()
        )
        self._index.compile()
        print(self._index.get_static_query("world hello"))
        # print(
        #     self._index.df,
        #     self._index.magnitudes,
        #     self._index.idf,
        #     self._index.tf,
        #     sep="\n",
        # )
        print("Base was compiled successfully")

    def get_files(self, fpath: str) -> list:
        result = []
        for f in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, f)):
                result.append(os.path.join(fpath, f))
        return result

    def query(self, query: str, directory: str) -> None:
        # check if index exist TODO FIX IT WITH DATEBASE

        if not os.path.exists(directory):
            self.parser.error("Can't find the directory")

        print("Loading answer...")
        self._index = ReverceIndexBuilder(
            directory, self.get_config().get_date_base_name()
        )
        if not self._index:
            self.parser.error("You should compile index first.")

        self._index.get_static_query(query)

    def detect_encoding(self, file_name: str) -> str:
        u = UniversalDetector()
        encoding = "UTF8"
        with open(file_name, "rb") as f:
            for line in f.readlines():
                u.feed(line)
        u.close()
        if u.result["encoding"]:
            encoding = u.result["encoding"]
        else:
            self.parser.error("Wrong encoding")

        return encoding


if __name__ == "__main__":
    # TODO replace sqlite queries to static class, less coherence
    Application()
