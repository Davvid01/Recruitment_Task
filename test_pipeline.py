import pandas as pd
import pytest

from pipeline import INPUT_FILE, clean_sales_data, run_pipeline

COLUMNS = ["Order ID", "Region", "Product", "Quantity ", "Unit Price", "Discount", "Order Date"]

ROWS = [
    ["SO-1", " south", "Mouse", "1 000", "29,50", "", "2026-01-01"],
    ["SO-2", "South", "Mouse", "2", "", "5.00", "2026-01-02"],
    ["SO-2", "South", "Mouse", "2", "", "5.00", "2026-01-02"],
    ["SO-3", "South", "Mouse", "-1", "29.50", "", "2026-01-03"],
    ["Order ID", "Region", "Product", "Quantity", "Unit Price", "Discount", "Order Date"],
    ["TOTAL", "", "", "1001", "", "5.00", ""],
]


def make_raw_df() -> pd.DataFrame:
    return pd.DataFrame(ROWS, columns=COLUMNS)


def test_clean_sales_data():
    df = clean_sales_data(make_raw_df())

    assert len(df) == 3
    assert df["region"].tolist() == ["South", "South", "South"]
    assert df["quantity"].tolist() == [1000, 2, -1]
    assert df["unit_price"].tolist() == [29.5, 29.5, 29.5]
    assert df["discount"].tolist() == [0.0, 5.0, 0.0]


def test_missing_price_without_reference_raises_error():
    raw = pd.DataFrame([["SO-1", "East", "Desk", "1", "", "", "2026-01-01"]], columns=COLUMNS)
    with pytest.raises(ValueError):
        clean_sales_data(raw)


def test_run_pipeline(tmp_path):
    input_file = tmp_path / "sales.csv"
    output_file = tmp_path / "revenue_by_region.csv"
    make_raw_df().to_csv(input_file, index=False)

    run_pipeline(input_file, output_file)
    result = pd.read_csv(output_file)

    assert result["region"].tolist() == ["South"]
    assert result["revenue"].tolist() == [29524.5]


def test_run_pipeline_on_real_sales_file(tmp_path):
    output_file = tmp_path / "revenue_by_region.csv"
    result = run_pipeline(INPUT_FILE, output_file)

    assert output_file.exists()
    assert result["region"].tolist() == ["Central", "East", "North", "South", "West"]
    assert round(result["revenue"].sum(), 2) == 2570247.03