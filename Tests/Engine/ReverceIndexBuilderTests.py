import pytest
import tempfile
import os

from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder

DIR = '\\TESTDIRfiles'


def set_up():
    with tempfile.TemporaryDirectory() as directory:
        with tempfile.NamedTemporaryFile() as f:
            pass


def NOtest_index_empty_file():
    with tempfile.NamedTemporaryFile() as f:
        b = ReverceIndexBuilder([f.name])
        result = b.builder_init()
        assert f in result


def test_find_from_C_file():
    d = os.getcwd() + DIR + "\\Hello World.txt"
    b = ReverceIndexBuilder([d])
    b.compile()
    assert "hello" in b.index
