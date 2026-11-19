import string

import pandas as pd

ALLOWED_CHARS = set(string.ascii_letters + "_")
OPERATORS = "+-*"


def is_valid_label(label: object) -> bool:
    if not isinstance(label, str) or not label:
        return False
    return all(char in ALLOWED_CHARS for char in label)


def parse_role(role: str) -> tuple[list[str], list[str]]:
    labels = []
    operators = []
    current = ""

    for char in role:
        if char in OPERATORS:
            labels.append(current.strip())
            operators.append(char)
            current = ""
        else:
            current += char

    labels.append(current.strip())
    return labels, operators


def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:
    empty = pd.DataFrame([])

    if not isinstance(df, pd.DataFrame) or not isinstance(role, str):
        return empty

    if not is_valid_label(new_column):
        return empty

    columns = df.columns.tolist()
    if not all(is_valid_label(col) for col in columns):
        return empty

    labels, operators = parse_role(role)
    for label in labels:
        if not is_valid_label(label) or columns.count(label) != 1:
            return empty

    # Step 1: evaluate all multiplications first
    terms = [df[labels[0]]]
    add_sub_ops = []

    for op, label in zip(operators, labels[1:]):
        if op == "*":
            terms[-1] = terms[-1] * df[label]
        else:
            add_sub_ops.append(op)
            terms.append(df[label])

    # Step 2: evaluate remaining additions and subtractions left-to-right
    total = terms[0]
    for op, term in zip(add_sub_ops, terms[1:]):
        if op == "+":
            total = total + term
        else:
            total = total - term

    result = df.copy()
    result[new_column] = total
    return result