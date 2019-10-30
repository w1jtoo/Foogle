from App.Terminal.Teminal import Terminal
from App.Config import Config
import argparse
import sys
import os.path
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Common.DateBase.BaseProvider import BaseProvider
from chardet import UniversalDetector
from App.Common.utils import get_files, filter_files
from pathlib import Path


class Foogle:
    def __init__(self, parser):
        self.parser = parser

        # TODO Subparser compile and query and add_parser
        # self.terminal = Terminal(self.container)

    def init_container(self):
        pass

    def get_config(self) -> Config:
        return Config()

    def compile(self, directory="") -> None:
        self.create_datebase_directory(self.get_config().get_general_path())
        self.base_provider = BaseProvider(
            os.path.join(
                self.get_config().get_general_path(),
                self.get_config().get_date_base_name(),
            )
        )
        print(f"Starting scaning {directory}...")
        files = filter_files(
            get_files(directory), self.get_config().get_types()
        )
        print(f"Found {len(files)} files to build index in.")

        self._index = ReverceIndexBuilder(files, self.base_provider)
        self.base_provider.recompile()
        self.fill_in_encoding_base(directory)
        print("Start of reverce index building...")
        self._index.compile()

        print("Base was compiled successfully")

    def fill_in_encoding_base(self, directory: str) -> None:
        for path in get_files(directory):
            self.base_provider.add_encoding_file(path, self.detect_encoding(path))

    def query(self, query: str, ranking: bool, directory="") -> None:
        self.base_provider = BaseProvider(
            os.path.join(
                self.get_config().get_general_path(),
                self.get_config().get_date_base_name(),
            )
        )

        if not directory:
            directory = os.path.abspath(Path.cwd())

        directory = os.path.join(directory)
        if not os.path.exists(directory):
            self.parser.error(f"Can't find the directory '{directory}'")

        print("Loading answer...")
        if not self.base_provider.is_valid():
            self.parser.error("You should compile index first.")

        self._index = ReverceIndexBuilder(get_files(directory), self.base_provider)
        result = self._index.get_static_query(query, ranking)
        if result:
            print("Result files:\n" + "\n".join(result))
        else:
            print("No coincidences was found.")

    def create_datebase_directory(self, db_path: str) -> None:
        if not os.path.exists(db_path):
            os.mkdir(db_path)

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
        description="File finder based on TF-IDF query searching. ",
        usage="Foogle --query [<dir>]",
    )
    subprasers = parser.add_subparsers(dest="command")
    find = subprasers.add_parser("find", help="Make query request.")
    find.add_argument(
        "--ranking",
        nargs="?",
        const=True,
        default=False,
        help="find with ranking (default: no ranking request)",
    )

    find.add_argument("query", nargs="+", help="Words that will be found.", type=str)

    _compile = subprasers.add_parser("compile", help="Compile query base.")
    _compile.add_argument("dir", help="Directory where query will be done.", type=str)

    args = parser.parse_args()
    foogle = Foogle(parser)

    if args.command == "find":
        print("".join(args.query))
        foogle.query("".join(args.query), args.ranking)
    elif args.command == "compile":
        print(args.dir)
        foogle.compile(args.dir)
    else:
        parser.print_help()
        exit()
