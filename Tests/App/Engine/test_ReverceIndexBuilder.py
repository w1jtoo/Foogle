from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Common.DateBase.BaseProvider import (
    BaseProvider,
    DateBase,
    TermsPathsItermator,
)
from Tests.TestUtils import DateBaseEntity

from App.Common.utils import get_files, filter_files


import pytest
import tempfile
import os

FILES_DIR = os.path.abspath("Tests/environment/files")

DATEBASE = os.path.abspath("Tests/environment/foogletempbase.db")


def test_index_compile():
    with DateBaseEntity(DATEBASE):
        with BaseProvider(DATEBASE) as bp:
            bp.recompile()
            index = ReverceIndexBuilder(
                filter_files(get_files(FILES_DIR), ["text/plain"]), bp
            )
            index.compile()

            assert (
                index.get_static_query("hello world", True)
                and index.get_static_query("world hello", True)
                and index.get_static_query("hello", True)
                and not index.get_static_query("gghhgghh", True)
                and not index.get_static_query("", True)
            )


def test_static_params():
    query_result = {"world hello": []}
    with DateBaseEntity(DATEBASE):
        with BaseProvider(DATEBASE) as bp:
            bp.recompile()
            index = ReverceIndexBuilder(
                filter_files(get_files(FILES_DIR), ["text/plain"]), bp
            )
            index.compile()

            assert set(index.get_static_query("hello world", False)) == set(
                index.get_static_query("world hello", False)
            )
