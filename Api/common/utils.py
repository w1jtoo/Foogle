import glob
from os import path
from os import getcwd


PATHS = []


def find_paths(directory: str) -> dict:
    """ Return dict consists from pairs: (dir, file),
        where file is foofile.
    """
    tpaths = glob.glob(directory + r'\**', recursive=True)

    return tpaths


if __name__ == "__main__":

    cwd = getcwd()
    print(find_paths(cwd))
