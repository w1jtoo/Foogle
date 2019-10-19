from Tests.TestUtils import DateBaseEntity
from App.Common.DateBase.BaseProvider import (
    BaseProvider,
    DateBase,
    TermsPathsItermator,
)
from App.Common.DateBase.SelectError import SelectError

import pytest

BASE_NAME = "test_date_base.bs"


def test_DateBase_string_format():
    # string formate of DateBase should include it's name
    assert (
        str(DateBase.INDEX).find("index") + 1
        and str(DateBase.IDF).find("idf") + 1
        and str(DateBase.TF).find("tf") + 1
        and str(DateBase.ENCODING).find("encoding") + 1
    )


def test_inialize_BaseProvider():
    with DateBaseEntity(BASE_NAME):
        BaseProvider(BASE_NAME)


def test_inialize_tables_is_empty():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_file_encoding()
            bp.initalize_idf_base()
            bp.initalize_tf_base()
            bp.initialize_index_base()

            assert (
                not bp.select_all(DateBase.ENCODING)
                and not bp.select_all(DateBase.IDF)
                and not bp.select_all(DateBase.TF)
                and not bp.select_all(DateBase.INDEX)
            )


def test_add_and_get_encoding():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_file_encoding()
            bp.add_encoding_file("word", "UTF8")

            assert bp.get_encoding("word") == "UTF8"


def test_get_nonexistent_encoding():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_file_encoding()

            with pytest.raises(SelectError):
                bp.get_encoding("word")


def test_drop_table_tables():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_file_encoding()
            bp.drop_table(DateBase.ENCODING)


def test_drop_tables():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_file_encoding()

            bp.drop_tables()

            bp._connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            assert not bp._cursor.fetchall()


def test_drop_table_nonexistent_table_should_not_raise_exeption():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.drop_table(DateBase.ENCODING)
            bp.drop_table(DateBase.IDF)
            bp.drop_table(DateBase.TF)
            bp.drop_table(DateBase.INDEX)

            bp._connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            assert not bp._cursor.fetchall()


# def test_get_terms():
#     with DateBaseEntity(BASE_NAME):
#         with BaseProvider(BASE_NAME) as bp:
#             bp.initialize_index_base()
#             bp.insert_into(DateBase.INDEX, "vasya", "\\home.txt", "12")

#             assert bp.get_terms_and_paths() == [("vasya", "\\home.txt")]


values = [
    ("vasya", "\\home.txt", 0, 0),
    ("is", "\\home.txt", 1, 1),
    ("a good", "\\home.txt", 2, 2),
    ("boy", "\\home.txt", 3, 3),
]


def test_secet_count_all_and_logic():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert (
                bp.select_count(DateBase.INDEX) == 4
                and bp.select_count(DateBase.INDEX, where="path='\\home.txt'") == 4
                and bp.select_count(DateBase.INDEX, where="path='nonpath'") == 0
                and bp.select_count(DateBase.INDEX, where="word='vasya'") == 1
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

            assert bp.select_one(DateBase.INDEX, where="word='vasya'") == (
                "vasya",
                "\\home.txt",
                0,
                0,
            )


def test_select_distinct():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:

            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            assert bp.select_distinct(DateBase.INDEX, distinct_params="path") == [
                ("\\home.txt",)
            ]


def test_terms_paths_iterator():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initialize_index_base()
            for value in values:
                bp.insert_into(DateBase.INDEX, *value)

            terms = bp.get_terms_paths_iterator()

            excepted_terms = list(terms)

            assert excepted_terms == [(value[0], value[1]) for value in values]


values_idf = [("vasya", 0), ("is", 1), ("a good", 2.2), ("boy", 3.3)]


def test_terms_iterator():
    with DateBaseEntity(BASE_NAME):
        with BaseProvider(BASE_NAME) as bp:
            bp.initalize_idf_base()
            for value in values_idf:
                bp.insert_into(DateBase.IDF, *value)

            terms = bp.get_terms_iterator()

            excepted_terms = list(terms)

            assert excepted_terms == [value[0] for value in values]
