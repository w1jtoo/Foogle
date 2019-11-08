from Tests.TestUtils import DateBaseEntity
from App.Common.DateBase.BaseProvider import (
    BaseProvider,
    DateBase,
    TermsPathsItermator,
)
from App.Common.DateBase.SelectError import SelectError

import pytest

BASE_NAME = "test_date_base.bs"
NONEXISTENT_NAME = "bacelscat.bs"


def test_DateBase_string_format():
    # string formate of DateBase should include it's name
    assert (
        str(DateBase.INDEX).find("index") + 1
        and str(DateBase.IDF).find("idf") + 1
        and str(DateBase.TF).find("tf") + 1
    )


def test_inialize_BaseProvider():
    with DateBaseEntity(BASE_NAME):
        BaseProvider(BASE_NAME)


def test_inialize_tables_is_empty():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_idf_base()
            bp.initalize_tf_base()
            bp.initialize_index_base()

            assert (
                not bp.select_all(DateBase.IDF)
                and not bp.select_all(DateBase.TF)
                and not bp.select_all(DateBase.INDEX)
            )


def test_drop_table_tables():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_idf_base()
            bp.drop_table(DateBase.IDF)


def test_drop_tables():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_idf_base()

            bp.drop_tables()

            bp._connection.execute(
                "SELECT name FROM \
                sqlite_master WHERE type='table'"
            )
            assert not bp._cursor.fetchall()


def test_drop_table_nonexistent_table_should_not_raise_exeption():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.drop_table(DateBase.IDF)
            bp.drop_table(DateBase.TF)
            bp.drop_table(DateBase.INDEX)

            bp._connection.execute(
                "SELECT name FROM sqlite_master \
                    WHERE type='table'"
            )
            assert not bp._cursor.fetchall()


def test_recompile():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.recompile()


values = [
    ("vasya", "\\home.txt", 0, 1, 1),
    ("is", "\\home.txt", 1, 2, 2),
    ("a good", "\\home.txt", 2, 3, 3),
    ("boy", "\\home.txt", 3, 4, 4),
]


def test_secet_count_all_and_logic():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert (
                bp.select_count(DateBase.INDEX) == 4
                and bp.select_count(
                    DateBase.INDEX,
                    where="path=?",
                    where_params=(values[0][1],),
                )
                == 4
                and bp.select_count(
                    DateBase.INDEX, where="path=?", where_params=("123",)
                )
                == 0
                and bp.select_count(
                    DateBase.INDEX,
                    where="word=?",
                    where_params=(values[0][0],),
                )
                == 1
            )


def test_secet_count_zero_items():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initialize_index_base()

            assert not bp.select_count(DateBase.INDEX)


def test_select_all():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert bp.select_all(DateBase.INDEX) == values


def test_select_one():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert bp.select_one(
                DateBase.INDEX, where="word=?", where_params=("vasya",)
            ) == ("vasya", "\\home.txt", 0, 1, 1)


def test_select_distinct():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert bp.select_distinct(
                DateBase.INDEX, distinct_params="path"
            ) == [("\\home.txt",)]


def test_terms_paths_iterator():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            terms = bp.get_terms_paths_iterator()

            excepted_terms = list(terms)

            assert set(excepted_terms) == set(
                [(value[0], value[1]) for value in values]
            )


def test_terms_iterator():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            terms = bp.get_terms_iterator()

            excepted_terms = list(terms)

            assert excepted_terms == [value[0] for value in values]


def test_is_valid_empty_base():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            assert not bp.is_valid()
