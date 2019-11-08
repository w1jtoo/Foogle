from App.Config import Config
import argparse
import sys
import os.path
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Common.DateBase.BaseProvider import BaseProvider
from App.Common.utils import get_files, filter_files
from pathlib import Path
from App.Terminal.Terminal import Terminal


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
		Terminal().sprint(f"Starting scaning {directory}...")
		files = filter_files(
			get_files(directory), self.get_config().get_types()
		)
		Terminal().sprint(f"Found {len(files)} files to build index in.")

		self._index = ReverceIndexBuilder(files, self.base_provider)

		self.base_provider.recompile()
		Terminal().sprint("Start of reverce index building...")
		self._index.compile()

		Terminal().sprint("Base was compiled successfully")



	def query(
		self, query: str, ranking: bool, directory="", date_base_directory=""
	) -> None:

		if not date_base_directory:
			date_base_directory = os.path.join(
				self.get_config().get_general_path(),
				self.get_config().get_date_base_name(),
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

		self._index = ReverceIndexBuilder(
			get_files(directory), self.base_provider
		)
		result = self._index.get_static_query(query, ranking)
		if result:
			Terminal().sprint("Result files:\n" + "\n".join(result))
		else:
			Terminal().sprint("No coincidences was found.")

	def create_datebase_directory(self, db_path: str) -> None:
		if not os.path.exists(db_path):
			os.mkdir(db_path)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="File finder based on TF-IDF query searching. ",
		usage="foogle.py [copile | find] [<optional args>]",
	)
	subprasers = parser.add_subparsers(dest="command")
	find = subprasers.add_parser("find", help="Make query request.")
	find.add_argument(
		"--noranking",
		nargs="?",
		const=True,
		default=False,
		help="find withought ranking (default: ranking request)",
	)

	find.add_argument(
		"query", nargs="+", help="Words that will be found.", type=str
	)

	_compile = subprasers.add_parser("compile", help="Compile query base.")
	_compile.add_argument(
		"dir", help="Directory where query will be done.", type=str
	)

	args = parser.parse_args()
	foogle = Foogle(parser)

	if args.command == "find":
		foogle.query("".join(args.query), args.noranking)
	elif args.command == "compile":
		foogle.compile(args.dir)
	else:
		parser.print_help()
		exit()
