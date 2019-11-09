from typing import Dict
import operator

class Query:
	operators_preority = {"|": 1, "&": 1, "!": 1, "(": 0, ")": 0}

	def __init__(self, query: str, total_set: set) -> None:
		self.query = query.split()
		self.total_set = total_set

	def _convert_to_postfix(self) -> str:
		result = []
		stack: list = []
		for word in self.query:
			if word in self.operators_preority:
				if len(stack) > 0 and word != "(":
					if word == ")":
						peek = stack.pop()
						while peek != "(":
							result.append(peek)
							peek = stack.pop()
					elif self.operators_preority[word] > self.operators_preority[stack[-1]]:
						stack.append(word)
					else:
						while len(stack) > 0 \
							and self.operators_preority[word] <= self.operators_preority[stack[-1]]:
							result.append(stack.pop())
						stack.append(word)
				else:
					stack.append(word)
			else:
				result.append(word)
			
		if len(stack):
			for word in stack:
				result.append(word)
		return " ".join(result)

	def calulate_expretion(self, op: str, stack, method):
		if op == "|":
			return method(stack.pop()) | method(stack.pop())
		elif op == "&":
			return method(stack.pop()) | method(stack.pop())
		elif op == "!":
			return self.total_set - method(stack.pop())
		else:
			raise Exception()


	def _culculate(self, postfix: str,method):
		stack = []
		queue = postfix.split()
		word = queue.pop(0)
		
		while queue:
			if word not in self.operators_preority:
				stack.append(word)
				word = queue.pop(0)
			else:
				local_result =  self.calulate_expretion(word, stack, method)
				stack.append(local_result)
				if queue:
					word = queue.pop(0)
				else:
					break

		return stack.pop()