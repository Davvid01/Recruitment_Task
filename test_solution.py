import pandas as pd

from solution import add_virtual_column


def test_precedence_and_immutability():
    df = pd.DataFrame({"a": [10, 5], "b": [2, 3], "c": [3, 2], "d": [1, 1]})
    original = df.copy()

    result = add_virtual_column(df, "a - b * c + d", "out")

    assert result["out"].tolist() == [5, 0]
    assert df.equals(original)


def test_invalid_unused_df_column_returns_empty():
    df = pd.DataFrame({"bad col": [1, 2], "a": [3, 4]})
    assert add_virtual_column(df, "a + a", "out").empty


def test_duplicate_column_in_role_returns_empty():
    df = pd.DataFrame([[1, 2]], columns=["a", "a"])
    assert add_virtual_column(df, "a + a", "out").empty


def test_malformed_roles_return_empty():
    df = pd.DataFrame({"a": [1], "b": [2]})

    assert add_virtual_column(df, "", "out").empty
    assert add_virtual_column(df, "   ", "out").empty
    assert add_virtual_column(df, "-a + b", "out").empty
    assert add_virtual_column(df, "a +", "out").empty
    assert add_virtual_column(df, "a / b", "out").empty
    assert add_virtual_column(df, "a + 5", "out").empty