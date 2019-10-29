import os

from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from Foogle import Foogle

FILES_DIR = os.path.abspath("Tests/environment/files")
DATEBASE = os.path.abspath("Tests/environment/foogletempbase.db")


def test_true():
    assert 1, "it's true"
