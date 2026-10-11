
import re
import sys


class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}
TOKEN_RE = re.compile(r"\s*(\d+\.?\d*|\.\d+|[-+*/()])")


def tokenize(expression):
    """Split an expression into numbers, operators and parentheses.
    A '-' or '+' in a unary position becomes 'neg' / 'pos' markers
    so that expressions such as -3 + 5 or 2 * (-4) work."""
    tokens, pos = [], 0
    expression = expression.rstrip()
    while pos < len(expression):
        m = TOKEN_RE.match(expression, pos)
        if not m:
            raise ValueError(f"invalid character '{expression[pos:].strip()[0]}'")
        tokens.append(m.group(1))
        pos = m.end()
    result = []
    for i, tok in enumerate(tokens):
        prev = result[-1] if result else None
        unary_position = prev is None or prev in PRECEDENCE or prev in ("(", "neg", "pos")
        if tok in ("-", "+") and unary_position:
            result.append("neg" if tok == "-" else "pos")
        else:
            result.append(tok)
    return result


def apply_operator(operators, values):
    """Pop one operator and its operand(s), push the result on the value stack."""
    op = operators.pop()
    if op == "neg":
        values.push(-values.pop())
        return
    if op == "pos":
        return
    right, left = values.pop(), values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        values.push(left / right)


def evaluate(expression):
    """Evaluate an infix expression using an operand stack and an operator stack."""
    values, operators = Stack(), Stack()
    try:
        for tok in tokenize(expression):
            if tok[0].isdigit() or tok[0] == ".":
                values.push(float(tok))
            elif tok in ("neg", "pos"):
                operators.push(tok)           # prefix operator, highest precedence
            elif tok == "(":
                operators.push(tok)
            elif tok == ")":
                while not operators.is_empty() and operators.peek() != "(":
                    apply_operator(operators, values)
                if operators.is_empty():
                    raise ValueError("mismatched parentheses")
                operators.pop()               # discard '('
                while not operators.is_empty() and operators.peek() in ("neg", "pos"):
                    apply_operator(operators, values)
            else:                             # binary operator + - * /
                while (not operators.is_empty() and operators.peek() != "("
                       and (operators.peek() in ("neg", "pos")
                            or PRECEDENCE[operators.peek()] >= PRECEDENCE[tok])):
                    apply_operator(operators, values)
                operators.push(tok)
        while not operators.is_empty():
            if operators.peek() == "(":
                raise ValueError("mismatched parentheses")
            apply_operator(operators, values)
        result = values.pop()
        if not values.is_empty():
            raise ValueError("invalid expression")
    except IndexError:
        raise ValueError("invalid expression")
    return result


def format_number(x):
    """Show whole numbers without a trailing .0, others to at most 6 decimals."""
    if x == int(x):
        return str(int(x))
    return f"{x:.6f}".rstrip("0").rstrip(".")


def is_separator(line):
    return re.fullmatch(r"-{3,}", line.strip()) is not None


def process_file(input_path, output_path):
    """Read expressions, evaluate each, and write results with the same separators."""
    with open(input_path, "r") as f:
        lines = [ln.rstrip("\n") for ln in f]

    out_lines = []
    for line in lines:
        if is_separator(line):
            out_lines.append(line.strip())    # keep the same separator
        elif line.strip() == "":
            continue                          # ignore blank lines
        else:
            try:
                out_lines.append(format_number(evaluate(line)))
            except (ValueError, ZeroDivisionError) as err:
                out_lines.append(f"Error: {err}")

    with open(output_path, "w") as f:
        f.write("\n".join(out_lines) + "\n")
    return out_lines


if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    results = process_file(in_file, out_file)
    print(f"Done. {len(results)} lines written to {out_file}")
