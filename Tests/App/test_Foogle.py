import pytest
import tempfile
import os

from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from Foogle import Foogle

FILES_DIR = os.path.join(
    "C:/Users/w1jtoo/Desktop/programming/python/tasks/Foogle/Tests/env/files"
)

DATEBASE = os.path.join(
    "C:/Users/w1jtoo/Desktop/programming/python/tasks/Foogle/Tests/env/foogletempbase.db"
)


def test_true():
    assert 1, "it's true"
