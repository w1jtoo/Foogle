from App.Common.Query import Query

names = set(["Vasya", "Dima", "Ilya"])
exmaple_to_calculate = "Vasya & Dima | Ilya"


def test_initialization_of_query():
	q = Query(exmaple_to_calculate, names)
	# q.result()


def test_convert_to_postfix():
	q = Query(exmaple_to_calculate, names)
	postfix = q._convert_to_postfix()
	p = Query("( a | b ) & c  | d", set())
	complex_postfix = p._convert_to_postfix()
	assert (
		postfix == "Vasya Dima & Ilya |" and complex_postfix == "a b | c & d |"
	)


def test_from_postfix():
	q = Query(exmaple_to_calculate, names)
	postfix = q._convert_to_postfix()

	result = q._culculate(postfix, lambda x: set([x]))

	assert result == "Ilya"
