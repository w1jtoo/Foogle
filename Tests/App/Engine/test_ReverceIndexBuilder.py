from App.FoogleEngine.ReverceIndexBuilder import ReverceIndexBuilder
from App.Common.DateBase.BaseProvider import (
    BaseProvider,
    DateBase,
    TermsPathsItermator,
)
from Tests.TestUtils import DateBaseEntity

from App.Common.utils import get_files


import pytest
import tempfile
import os

FILES_DIR = os.path.abspath(
    "C:\\Users\\w1jtoo\\Desktop\\programming\\python\\tasks\\Foogle\\Tests\\env\\files"
)

DATEBASE = os.path.abspath(
    "C:\\Users\\w1jtoo\\Desktop\\programming\\python\\tasks\\Foogle\\Tests\\env\\foogletempbase.db"
)


def test_index_compile():
    with DateBaseEntity(DATEBASE):
        with BaseProvider(DATEBASE) as bp:
            bp.recompile()
            index = ReverceIndexBuilder(get_files(FILES_DIR), bp)
            index.compile()

            assert (
                index.get_static_query("hello world")
                and index.get_static_query("world hello")
                and index.get_static_query("hello")
                and not index.get_static_query("gghhgghh")
                and not index.get_static_query("")
            )


def test_static_params():
    query_result = {"world hello" : []}
    with DateBaseEntity(DATEBASE):
        with BaseProvider(DATEBASE) as bp:
            bp.recompile()
            index = ReverceIndexBuilder(get_files(FILES_DIR), bp)
            index.compile()

            assert (
                set(index.get_static_query("hello world"))
                == set(index.get_static_query("world hello"))
            )
