import argparse
import logging
import os.path
import sys
from pathlib import Path

from logdecorator import log_exception, log_on_end, log_on_error, log_on_start

from App.Common.DateBase.BaseProvider import BaseProvider
from App.Common.Query import Query
from App.Common.utils import filter_files, get_files
from App.Config import Config
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Terminal.Terminal import Terminal

# TODO make hint to update (recompile) db
class Foogle:
    def __init__(self, parser):
        self.parser = parser

    def initialize_logger(self) -> None:
        file_name = os.path.join(
            self.get_config().general_path, self.get_config().logging_file_name
        )
        # creating new file
        if not os.path.exists(self.get_config().general_path):
            os.mkdir(self.get_config().general_path)
        if not os.path.exists(file_name):
            f = open(file_name, "w")
            f.close()

        logging.basicConfig(
            format="%(asctime)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            filename=file_name,
            level=logging.DEBUG,
        )
        logging.info("logger initialization")

    def get_config(self) -> Config:
        return Config()

    @log_on_start(logging.DEBUG, "Start compile date base...")
    @log_on_error(
        logging.ERROR,
        "Error on compiling {e!r}",
        on_exceptions=Exception,
        reraise=True,
    )
    @log_on_end(logging.DEBUG, "Compiled successfully!")
    def compile(self, directory="") -> None:
        self.initialize_logger()
        self.create_datebase_directory(self.get_config().get_general_path())
        self.base_provider = BaseProvider(
            os.path.join(
                self.get_config().general_path, self.get_config().date_base_name,
            )
        )
        Terminal().sprint(f"Starting scaning {directory}...")
        files = filter_files(
            get_files(directory),
            self.get_config().types,
            self.get_config().extention_types,
        )
        Terminal().sprint(f"Found {len(files)} files to build index in.")
        if len(files):
            self._index = ReverceIndexBuilder(files, self.base_provider)

            self.base_provider.recompile()
            Terminal().sprint("Start of reverce index building...")
            self._index.compile()

            Terminal().sprint("Base was compiled successfully")
        else:
            Terminal().sprint("No files to compile date base.")

    @log_on_start(
        logging.DEBUG, "Starting '{query:s}' searching with ranking:{ranking:b}...",
    )
    @log_on_error(
        logging.ERROR,
        "Error on compiling  {query:s}-ranking:{ranking:b}: {e!r}",
        on_exceptions=Exception,
        reraise=True,
    )
    @log_on_end(
        logging.DEBUG,
        "Searching of '{query:s}' with ranking:{ranking:b} finished successfully!",
    )
    def query(
        self, query: str, ranking: bool, directory="", date_base_directory=""
    ) -> None:

        if not date_base_directory:
            date_base_directory = os.path.join(
                self.get_config().general_path, self.get_config().date_base_name,
            )

        self.base_provider = BaseProvider(date_base_directory)

        if not directory:
            directory = os.path.abspath(Path.cwd())
        else:
            directory = os.path.join(directory)

        if not os.path.exists(directory):
            self.parser.error(f"Can't find the directory '{directory}'")

        Terminal().sprint("Loading answer...")
        if not self.base_provider.is_valid():
            self.parser.error("You should compile index first.")

        files = self.base_provider.get_files()
        self._index = ReverceIndexBuilder(files, self.base_provider)

        result = Query(query, set(files)).make_result(
            lambda x: self._index.get_static_query(x, ranking)
        )

        if result:
            Terminal().sprint("Result files:\n" + "\n".join(result))
        else:
            Terminal().sprint("No coincidences was found.")

    def status(self, directory="", date_base_directory="") -> None:
        print_buffer = []

        if not date_base_directory:
            date_base_directory = os.path.join(
                self.get_config().general_path, self.get_config().date_base_name,
            )
        base_provider = BaseProvider(date_base_directory)

        if base_provider.is_valid():
            print_buffer.append(
                f" > Date base is valid and ready to work. Also it has: \
            \n  > {base_provider.get_paths_count()} registred paths. \
            \n  > path {base_provider.path} \
            \n  > size {os.stat(base_provider.path).st_size / 1024} kB \
            \n  > {base_provider.get_terms_count()} registred terms \
            "
            )
        else:
            print_buffer.append("Date Base is invalid. Recompile it please.")
        print_buffer.append("")
        print_buffer.append(f" > Configuration:")
        print_buffer.append(f"{'name':<20}{'value':<45}{'standart'}")
        for name in self.get_config().get_all_names():
            value = self.get_config().get_value(name)
            if type(value) is list:
                value = ",".join(value)
                if not value:
                    value = "empty"
            elif type(value) is int:
                value = str(value)
            print_buffer.append(
                f"{name:<20}{value:<30}\
                    { 'yes' if self.get_config().is_standart(name) else 'no':1}"
            )

        logger_path = os.path.join(
            self.get_config().general_path, self.get_config().logging_file_name
        )
        if os.path.exists(logger_path):
            print_buffer.append(
                f" > Logger initalized. Its size {os.stat(logger_path).st_size / 1024} kB"
            )
        else:
            print_buffer.append("Can't find logger. Looks like it wasn't init")
        # TODO add date base and logger creation time
        Terminal().sprint("\n".join(print_buffer))

    def create_datebase_directory(self, db_path: str) -> None:
        if not os.path.exists(db_path):
            os.mkdir(db_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="File finder based on TF-IDF query searching. ",
        usage="foogle.py [compile | find] [<optional args>]",
    )
    subprasers = parser.add_subparsers(dest="command")
    status = subprasers.add_parser(
        "status", help="Show status of registred files and other program files. "
    )
    find = subprasers.add_parser("find", help="Make query request.")
    find.add_argument(
        "--noranking",
        nargs="?",
        const=True,
        default=False,
        help="find withought ranking (default: ranking request)",
    )

    find.add_argument("query", nargs="+", help="Words that will be found.", type=str)

    _compile = subprasers.add_parser("compile", help="Compile query base.")
    _compile.add_argument("dir", help="Directory where query will be done.", type=str)

    args = parser.parse_args()
    foogle = Foogle(parser)

    if args.command == "find":
        foogle.query("".join(args.query), args.noranking)
    elif args.command == "compile":
        foogle.compile(args.dir)
    elif args.command == "status":
        foogle.status()
    else:
        parser.print_help()
        exit()
