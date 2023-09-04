from typing import List
import re
from copy import deepcopy
from time import sleep



class Operator:
    def __init__(self, character: str, name: str, priority: int, alternatives: List[str] = None):
        if alternatives is None:
            alternatives = []

        assert len(character) == 1
        assert len(name) > 0
        assert type(alternatives) == list

        self.character = character
        self.name = name
        self.priority = priority
        self.alternatives = alternatives

        return

    def __eq__(self, __value: object) -> bool:
        return __value == self.character or __value in self.alternatives

    def __str__(self) -> str:
        return f"({self.character:s}, {self.name:s})"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def get_priority(priority: int):
        global OPERATORS
        return filter(lambda item: item.priority == priority, OPERATORS)


BRACKET_OPEN = "(«"
BRACKET_CLOSE = ")»"

OPERATORS = [
    Operator("^", "power", 1, ["**"]),
    Operator("*", "multiply", 2, ["×"]),
    Operator("/", "divide", 2, ["÷"]),
    Operator("+", "add", 3),
    Operator("-", "subtract", 3),
    Operator("±", "plus_or_minus", 3),
    Operator("=", "equals", 0),
    Operator("<", "less_than", 0),
    Operator("≤", "less_than_or_equal", 0),
    Operator(">", "greater_than", 0),
    Operator("≥", "greater_than_or_equal", 0),

]

"+", "-", "±", "*", "=", ">", "<", "≥", "≤", "≠", "→", " ", ":"
# OPERATOR_ASSOCIATIVE = [set(["^", "**"]), set("*")]
ONE_ARGUMENT_FUNCTIONS = ["sqrt", "cos", "sin", "log", "ln"]
TWO_ARGUMENT_FUNCTIONS = ["add", "minus", "times", "divide"]

"""
This is the two argument function constant.
"""


class Parse:
    """
    This converts ASCIImath into a method that lets you list it as a parsed function.

    `math_string`: The ASCIImath string you would like to parse.
    """

    def __init__(self, math_string: str) -> None:
        self.input = math_string
        self.string = re.sub(r"\s\s", " ", deepcopy(math_string))
        self.prepare()
        return

    def __len__(self):
        return len(self.string)

    def __getitem__(self, item: int):
        if type(item) != int:
            raise TypeError(f"Indices must be of type `int`, not `{type(item).__name__:s}.`")
        if item < 0:
            raise IndexError(f"Min index is 0. You supplied {item:d}.")
        if item > len(self):
            raise IndexError(f"Max index is {len(self):d}. You supplied {item:d}.")
        return self.string[item]

    def find(self, pattern: str | re.Pattern[str]) -> tuple | None:
        """
        Returns the first matched index of ``self.string``.

        :param pattern: The pattern to match.
        :return: The first index if successful, None otherwise.
        :rtype: tuple | None

        """
        match = re.search(pattern, self.string)
        if match:
            return match.span()
        return None

    def find_final(self, pattern: str | re.Pattern[str]) -> tuple | None:
        """
        Returns the final matched index of ``self.string``.

        :param pattern: The pattern to match.
        :return: The first index if successful, ``None`` otherwise.
        :rtype: tuple | None
        """
        findings = re.finditer(pattern, self.string)
        match = None
        for item in findings:
            match = item.span()
        return match

    def replace(self, pattern: str | re.Pattern[str], replacement: str) -> None:
        """
        Replaces all occurrences of ``pattern`` with ``replacement``.

        :param pattern: The pattern to match.
        :param replacement: The string to substitute with.
        :return: Updates ``self.string``, ``None`` is returned.
        """
        self.string = re.sub(pattern, replacement, self.string)
        return None

    def insert(self, index: int, character: str) -> None:
        """
        Inserts ``character`` at the specified ``index``.

        :param index: The index to insert at.
        :param character: The character to insert.
        :return: Updates ``self.string``, ``None`` is returned.
        """
        assert len(character) == 1
        self.string = self.string[:index] + character + self.string[index:]
        return None

    def overwrite(self, index: int, character: str) -> None:
        """
        Substitutes in ``character`` at the specified ``index``.

        :param index: The index to overwrite as.
        :param character: The character to overwrite as.
        :return: Updates ``self.string``, ``None`` is returned.
        """
        assert len(character) == 1
        self.string = self.string[:index] + character + self.string[index + 1:]
        return

    def pop(self, indices: tuple) -> str:
        """
        Removes the characters between the specified ``index``.

        :param indices: A tuple comprised of the starting index and the ending index to grab from.
        :return: Updates ``self.string``, returns the portion you just extracted.
        """
        if type(indices) != tuple:
            raise TypeError(f"Indices must be of type `tuple`, not `{type(indices).__name__:s}.`")
        if len(indices) != 2:
            raise TypeError(f"Bad {len(indices)} element tuple. Tuples must store 2 integers.")

        output = self.string[indices[0]:indices[1]]
        self.string = self.string[:indices[0]] + self.string[indices[1]:]
        return output

    def prepare(self):
        print("Begin formatting")
        i = 0
        starting_index = 0
        bracket = 0

        count_bracket_opens = 0
        count_bracket_closes = 0

        match = self.find(r"\{")
        while match:
            count_bracket_opens += 1
            i = match[0]
            self.overwrite(i, "(")
            match = self.find(r"\{")

        match = self.find(r"\}")
        while match:
            count_bracket_closes += 1
            i = match[0]
            self.overwrite(i, ")")
            match = self.find(r"\}")

        if count_bracket_opens > count_bracket_closes:
            raise SyntaxError(f"There are {count_bracket_opens - count_bracket_closes} more '(' brackets than ')' characters in your input.")
        if count_bracket_opens < count_bracket_closes:
            raise SyntaxError(f"There are {count_bracket_closes - count_bracket_opens} more ')' brackets than '(' characters in your input.")
        print("End formatting")
        return

    def format(self):
        bracket = 0

        def bracket_eval(index: int):
            nonlocal bracket
            if self[index] in BRACKET_CLOSE:
                bracket += 1
            if self[index] in BRACKET_OPEN:
                bracket -= 1
            return


        for priority in range(0, 5):

            i = 0
            operation_list = list(Operator.get_priority(priority))
            print("Starting", priority, "pass")
            while i < len(self):

                if self[i] in operation_list:

                    a = i - 1
                    if self[a] == " ":
                        a -= 1

                    if self[a] in BRACKET_CLOSE:  # bracket already exists
                        bracket = 1
                        while a > 0:
                            bracket_eval(a)
                            if bracket == 0:
                                break
                            a -= 1
                        if a < 0:
                            raise SyntaxError(f"Unmatched ')' bracket at char {i:d}, '{self.string[i-1:i+2]}'\n{self.string}")

                    else:  # bracket doesn't exists
                        self.insert(a + 1, ")")
                        bracket = 1
                        while a > 0:
                            bracket_eval(a)
                            if bracket == 1:
                                if self[a] in operation_list:
                                    break
                            a -= 1
                        if bracket != 1:
                            raise SyntaxError(f"Unmatched ')' bracket at char {i:d}, '{self.string[i-1:i+2]}'\n{self.string}")
                        if a < 0:
                            a = 0

                        self.insert(a, "(")
                        i += 2






                    b = i + 1

                    print("Captured:", self.string[a:i])

                    #print("Found", self[i], "at", i)
                i += 1

            # breaks the priority
            break
        return


x = Parse(
    "x = -(-1478412 π a^2 f_57 + sqrt((-1478412 π a^2 f_57 - 54)^2 - 2916) - 54)^(1/3)/(702 2^(1/3) a) - 1/(39 2^(2/3) a (-1478412 π a^2 f_57 + sqrt((-1478412 π a^2 f_57 - 54)^2 - 2916) - 54)^(1/3)) + 1/(234 a)"
    #"433x 43 - 3 = 53 = 5"
)
print(x.string)

print()

x.format()

print(x.string)

