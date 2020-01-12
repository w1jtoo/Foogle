from App.Common.Query import Query

names = set(["Vasya", "Dima", "Ilya"])
exmaple_to_calculate = "Vasya & Dima | Ilya"


def test_initialization_of_query():
    q = Query(exmaple_to_calculate, names, split_pattern=lambda x: x.split())
    # q.result()


def to_postfix_notation(query: str, expected: str, total_set: set):
    p = Query(query, total_set, split_pattern=lambda x: x.split())
    postfix = p._convert_to_postfix()
    assert postfix == expected


def test_convert_to_postfix():
    to_postfix_notation("( a | b ) & c  | d", "a b | c & d |", set())
    to_postfix_notation("Vasya & Dima | Ilya", "Vasya Dima & Ilya |", set())
    to_postfix_notation("! 1 & 3", "1 ! 3 &", set())
    to_postfix_notation("! 1 & ! 0", "1 ! 0 ! &", set())
    to_postfix_notation("! ( 1 | 0 )", "1 0 | !", set())
    # same with string fomat
    to_postfix_notation("not ( 1 or 0 )", "1 0 or not", set())
    to_postfix_notation("not not not 1", "1 not not not", set())
    to_postfix_notation("( 1 or 0 )", "1 0 or", set())


def culculating_result(
    expretion: str, expected: str, total_set: set, method
) -> None:
    q = Query(expretion, total_set, split_pattern=lambda x: x.split())
    postfix = q._convert_to_postfix()
    print(postfix)
    result = q._culculate(postfix, method)
    assert result == expected


def test_culculating_result():
    culculating_result(
        "Vasya & Dima | Ilya", set(["Ilya"]), names, lambda x: [x]
    )
    culculating_result(
        "123 & 345", set("3"), set(range(10)), lambda x: list(x)
    )
    culculating_result(
        "! 1 & 3", set([3]), set(range(10)), lambda x: map(int, list(x))
    )
    culculating_result(
        "123", set(list("123")), set(range(10)), lambda x: list(x)
    )
    culculating_result(
        "0 & ! 1 | 2", set([0, 2]), set(range(4)), lambda x: map(int, list(x))
    )
    culculating_result(
        "! 1 & ! 0", set([3, 2]), set(range(4)), lambda x: map(int, list(x))
    )
    culculating_result(
        "0 and not 1 or 2",
        set([0, 2]),
        set(range(4)),
        lambda x: map(int, list(x)),
    )
    culculating_result(
        "( 0 or 1 )", set([0, 1]), set(range(4)), lambda x: map(int, list(x))
    )
    culculating_result(
        "not not 0", set([0]), set(range(4)), lambda x: map(int, list(x))
    )


def query_split(line: str, result: str) -> None:
    assert Query.split_pattern(line) == result


def test_query_split_method():
    query_split(
        "not Hobbit and 'Harry Potter'",
        ["not", "Hobbit", "and", "Harry Potter"],
    )
    query_split("not 'Hobbit'", ["not", "Hobbit"])
    query_split(
        "not (Hobbit and 'Harry Potter') or HW",
        ["not", "(", "Hobbit", "and", "Harry Potter", ")", "or", "HW"],
    )
    query_split("'Harry Potter'", ["Harry Potter"])
