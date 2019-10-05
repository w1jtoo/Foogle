from App.AppContainer import AppContainer
from App.Terminal.Teminal import Terminal
import argparse
from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder


class Application:
    def __init__(self):
        self.container = AppContainer()

        self.terminal = Terminal(self.container)

    def init_container(self):
        pass

    def run(self):
        raise NotImplementedError

    def comlipe_base(self, dir: str) -> None:
        pass

    def push_query(self, query: str) -> None:
        pass


parser = argparse.ArgumentParser(description="Foogle")

parser.add_argument("--action", choices=["compile", "find"], default="compile")

parser.add_argument("dir", metavar="dir", help="dir where query will be found")
parser.add_argument("query", metavar="query", help="what query should be found")


if __name__ == "__main__":
    args = parser.parse_args()
    app = Application()
    if args.action == "compile":
        app.comlipe_base(args.dir)
    elif args.action == "find":
        app.push_query(args.query)
