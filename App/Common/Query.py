import operator
from typing import Any, Iterable, List, Optional, Set


class Query:
    prefix_operators = {"!": 3, "not": 3}
    binary_operators = {"|": 2, "&": 2, "or": 2, "and": 2}
    left_brakets = {"(": 0, "[": 0, "{": 0}
    right_brakets = {")": 0, "]": 0, "}": 0}

    @staticmethod
    def get_operators() -> Set[str]:
        return (
            Query.binary_operators.keys()
            | Query.prefix_operators.keys()
            | Query.left_brakets.keys()
            | Query.right_brakets.keys()
        )

    def get_preority(self, key: str) -> Optional[int]:
        return (
            self.prefix_operators.get(key)
            or self.binary_operators.get(key)
            or self.right_brakets.get(key)
            or self.left_brakets.get(key)
        )

    @staticmethod
    def split_pattern(string: str) -> list:
        splited = string.strip() + " "
        result = []

        sep_item: List[str] = []
        is_with_comma = False
        after_space = False
        for index, token in enumerate(splited):
            if token in Query.get_operators() and (
                after_space or splited[index + 1] == " "
            ):
                result.append(token)
            elif token == "'":
                if is_with_comma:
                    is_with_comma = False
                    result.append("".join(sep_item))
                    sep_item = []
                else:
                    is_with_comma = True
            elif token == " ":
                if not is_with_comma:
                    if sep_item:
                        result.append("".join(sep_item))
                    sep_item = []
                else:
                    sep_item.append(" ")
                after_space = not after_space
            else:
                sep_item.append(token)
        if sep_item:
            result.append("".join(sep_item))

        return result

    def __init__(self, query: str, total_set: set, split_pattern=None) -> None:
        self.query = query

        if not split_pattern:
            self.splited = Query.split_pattern(self.query)
        else:
            self.splited = split_pattern(self.query)

        self.total_set = total_set

    def _convert_to_postfix(self) -> str:
        stack = []
        result = []
        for token in self.splited:
            if token in self.prefix_operators:
                stack.append(token)
            elif token in self.left_brakets:
                stack.append(token)
            elif token in self.right_brakets:
                while stack[-1] not in self.left_brakets:
                    result.append(stack.pop())
                stack.pop()
            elif token in self.binary_operators:
                while stack and (
                    stack[-1] in self.binary_operators
                    or self.get_preority(stack[-1]) > self.get_preority(token)
                ):
                    result.append(stack.pop())
                stack.append(token)
            else:
                result.append(token)

        while stack:
            token = stack.pop()
            if token in ["(", ")"]:
                continue
            result.append(token)

        return " ".join(result)

    def upzip_without_empty(self, stack, params_count: int, method):
        result: List[Any] = []
        for _ in range(params_count):
            element = stack.pop()
            if isinstance(element, set):
                result.append(element)
            else:
                result.append(set(method(element)))

        return result

    def calulate_expretion(self, op: str, stack: List, method):
        if op == "|" or op == "or":
            first, second = self.upzip_without_empty(stack, 2, method)
            result = first | second
        elif op == "&" or op == "and":
            first, second = self.upzip_without_empty(stack, 2, method)
            result = first & second
        elif op == "!" or op == "not":
            first = self.upzip_without_empty(stack, 1, method)[0]
            result = self.total_set - first
        else:
            raise Exception()

        return result

    def _culculate(self, postfix: str, method) -> Optional[set]:
        stack: List[Any] = []
        queue = postfix.split()

        for word in queue:
            if word in self.get_operators():
                local_result = self.calulate_expretion(word, stack, method)
                stack.append(local_result)
            else:
                stack.append(set(method(word)))

        return stack.pop()

    def make_result(self, method) -> Optional[set]:
        return self._culculate(self._convert_to_postfix(), method)
