import re
from collections import namedtuple
from enum import Enum, auto


class State(Enum):
    UNKNOWN = auto()
    OPERAND = auto()
    OPERATOR = auto()


class Associativity(Enum):
    LEFT = auto()
    RIGHT = auto()


opinfo = namedtuple("Operator", "precedence associativity")
operator_info = {
    "+": opinfo(0, Associativity.LEFT),
    "-": opinfo(0, Associativity.LEFT),
    "*": opinfo(1, Associativity.LEFT),
    "/": opinfo(1, Associativity.LEFT),
    "^": opinfo(2, Associativity.RIGHT),
}


def tokenize(input_string):
    """
    Parse the string representation of an arithmetic expression, and return tokens of
    operands, operators (+, -, *, /, ^) and parentheses, e.g., for value "1+2 * (3-4)" as the input_string,
    this function return a list ["1", "+", "2", "*", "(", "3", "-", "4", ")"]

    Args:
      input_string: string representation of the arithmetic expression
    Returns:
      a list of strings, representing operands and operators in the original order

    """
    cleaned = re.sub(r"\s+", "", input_string)
    chars = list(cleaned)
    output = []
    state = State.UNKNOWN
    buf = ""
    while len(chars) != 0:
        char = chars.pop(0)
        if char in ["(", ")"]:
            output.append(buf) if buf != "" else False
            buf = ""
            output.append(char)
        elif char in operator_info:
            if char == "-" and (state == State.OPERATOR or state == State.UNKNOWN):
                state = State.OPERAND
            else:
                state = State.OPERATOR
            output.append(buf) if buf != "" else False
            buf = char
        else:
            if state != State.OPERAND:
                output.append(buf) if buf != "" else False
                buf = ""
            state = State.OPERAND
            buf += char
    output.append(buf) if buf != "" else False
    return output


def shunt(tokens):
    """
    Dijkstra's Shunting Yard Algorithm to convert infix notation to postfix notation (aka. reverse Polish notation)
    e.g. this function will return ['1', '2', '3', '*', '+'] for input tokens of ["1", "+", "2", "*", "3"].
    NOTE: postfix notation does not have parentheses

    Args:
      tokens: a list of operands and operators in order for the infix notation of an arithmetic expression
    Returns:
      the list of operands and operators in postfix notation order

    """
    tokens += ["end"]
    operators = []
    output = []
    while len(tokens) != 1:
        current_token = tokens.pop(0)
        if current_token in operator_info.keys():
            while True:
                if len(operators) == 0:
                    break
                satisfied = False
                if operators[-1] != "(":
                    if (
                        operator_info[operators[-1]].precedence
                        > operator_info[current_token].precedence
                    ):
                        # operator at top has greater precedence
                        satisfied = True
                    elif (
                        operator_info[operators[-1]].precedence
                        == operator_info[current_token].precedence
                    ):
                        if (
                            operator_info[operators[-1]].associativity
                            == Associativity.LEFT
                        ):
                            satisfied = True
                if not satisfied:
                    break
                output.append(operators.pop())
            operators.append(current_token)
        elif current_token == "(":
            operators.append(current_token)
        elif current_token == ")":
            while True:
                if len(operators) == 0:
                    break
                if operators[-1] == "(":
                    break
                output.append(operators.pop())
            if len(operators) != 0 and operators[-1] == "(":
                operators.pop()
        else:
            # is an operand
            output.append(current_token)

    output.extend(operators[::-1])
    return output


def restore(postfix_list):
    """

    Restore a infix version of the arithmetic expression without the unnecessary parenthese.
    Args:
      postfix_list: the list of operands/operators in the reverse Polish order
    Returns:
      a string representation of the arithmetic expression without the unnecessary parenthese.


    The basic idea of the algorithm is:
        We eval the postfix expression step by step (pivoting on operators one by one). 
        In each step, we always have a operator and two "operands", the operands could be either
        "basic" operands or expressions that includes operators/parenthese, and we will bind the operator
        and the two operands back to a infix order, and form a new operand and we could call the operator 
        "pivotal operator" for this new operand.

        When we work on an operator with their operands, we check the precedence of the current
        operator and the pivotal operators for both operands, and if the current operator has higher 
        precedence over the pivotal operator of either operands, we need to surrund the operand with
        a pair of parentheses.

        We also surround the right expression with parenthese when the current operator is - (substraction)
        or / (division) and the pivotal operator of the right expression has same precedence; this is because 
        substraction and division are both left associative only, and the evaluation result will be different
        with and without parentheses for the right expression.

    """
    # reconstruct the postfix_list so that we could keep track of the current pivotal operator
    # of the operand/expression. For basic operands, the pivotal operator is given a dummy value ""
    postfix_obj_list = [(v, "") for v in postfix_list]
    idx = 0
    while idx < len(postfix_obj_list):
        if postfix_obj_list[idx][0] in operator_info:
            if idx >= 2:
                new_expr = None
                if (
                    postfix_obj_list[idx - 2][1] != ""
                    and operator_info[postfix_obj_list[idx][0]].precedence
                    > operator_info[postfix_obj_list[idx - 2][1]].precedence
                ):
                    new_expr = "(" + postfix_obj_list[idx - 2][0] + ")"
                else:
                    new_expr = postfix_obj_list[idx - 2][0]

                new_expr += postfix_obj_list[idx][0]

                if postfix_obj_list[idx - 1][1] != "":
                    if operator_info[
                        postfix_obj_list[idx][0]
                    ].precedence > operator_info[
                        postfix_obj_list[idx - 1][1]
                    ].precedence or (
                        operator_info[postfix_obj_list[idx][0]].precedence
                        == operator_info[postfix_obj_list[idx - 1][1]].precedence
                        and (postfix_obj_list[idx][0] == "/" or postfix_obj_list[idx][0] == "-")
                    ):
                        new_expr += "(" + postfix_obj_list[idx - 1][0] + ")"
                    else:
                        new_expr += postfix_obj_list[idx - 1][0]

                else:
                    new_expr += postfix_obj_list[idx - 1][0]

                postfix_obj_list = (
                    postfix_obj_list[: idx - 2]
                    + [(new_expr, postfix_obj_list[idx][0])]
                    + postfix_obj_list[idx + 1:]
                )
                idx = idx - 2
        else:
            idx += 1

    return postfix_obj_list[0][0]


def remove_unnecessary_parentheses(input_expr):
    return restore(shunt(tokenize(input_expr)))


def run_test():
    assert remove_unnecessary_parentheses("1 +  (2 * 3)") == "1+2*3"
    assert remove_unnecessary_parentheses("1*(2+(3*(4+5)))") == "1*(2+3*(4+5))"
    assert remove_unnecessary_parentheses("2 + (3 / -5)") == "2+3/-5"
    assert remove_unnecessary_parentheses("(2 + ((3 / (-5))))") == "2+3/-5"
    assert remove_unnecessary_parentheses(
        "x123+(y+z)+(t+(v+w))") == "x123+y+z+t+v+w"
    assert remove_unnecessary_parentheses("2 + (3^3)") == "2+3^3"
    assert remove_unnecessary_parentheses(
        "-2 + (3 - 2) - 2* 3") == "-2+3-2-2*3"
    assert remove_unnecessary_parentheses(
        "-2 + (3 * 2) - 2* 3") == "-2+3*2-2*3"
    assert remove_unnecessary_parentheses("7+12/(4*2)") == "7+12/(4*2)"
    assert remove_unnecessary_parentheses("-14-12/(4/2)") == "-14-12/(4/2)"
    assert (
        remove_unnecessary_parentheses("(x1+y1)*(x2*y2-(x3*y3))")
        == "(x1+y1)*(x2*y2-x3*y3)"
    )


if __name__ == "__main__":
    while True:
        user_input = input("Input:")
        if user_input == "quit":
            break
        elif user_input == "run_test":
            run_test()
            print("All test pass")
        else:
            print("Output: " + remove_unnecessary_parentheses(user_input))
