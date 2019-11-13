import os

from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from foogle import Foogle
import pytest

FILES_DIR = os.path.abspath("Tests/environment/files")
DATEBASE = os.path.abspath("Tests/environment/foogletempbase.db")

# TODO write tests
# def test_foogle_initialization():
#     with pytest.raises(TypeError):
#         Foogle()
