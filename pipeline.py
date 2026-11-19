from pathlib import Path

import pandas as pd

from solution import add_virtual_column

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "sales.csv"
OUTPUT_FILE = BASE_DIR / "revenue_by_region.csv"


def clean_sales_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.astype(str)
    df.columns = [name.strip().lower().replace(" ", "_") for name in df.columns]

    # Remove repeated mid-file header and summary TOTAL footer row
    order_id = df["order_id"].str.strip()
    df = df[(order_id != "Order ID") & (order_id != "TOTAL")].copy()

    df["order_id"] = df["order_id"].str.strip()
    df["region"] = df["region"].str.strip().str.title()
    df["product"] = df["product"].str.strip()
    df["order_date"] = df["order_date"].str.strip()

    df["quantity"] = df["quantity"].str.replace(" ", "").astype(int)

    df["unit_price"] = pd.to_numeric(
        df["unit_price"].str.replace(",", "."), errors="coerce"
    )
    price_by_product = df.groupby("product")["unit_price"].first()
    df["unit_price"] = df["unit_price"].fillna(df["product"].map(price_by_product))
    if df["unit_price"].isna().any():
        raise ValueError("Missing unit_price for a product with no reference price.")

    df["discount"] = pd.to_numeric(
        df["discount"].str.replace(",", ".").replace("", "0")
    )

    # Deduplicate after text normalization so whitespace/casing variants are caught
    df = df.drop_duplicates()

    return df.reset_index(drop=True)


def run_pipeline(
    input_path: Path = INPUT_FILE, output_path: Path = OUTPUT_FILE
) -> pd.DataFrame:
    raw_df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    clean_df = clean_sales_data(raw_df)

    df = add_virtual_column(clean_df, "quantity * unit_price - discount", "revenue")
    if df.empty:
        raise ValueError("Failed to compute 'revenue' column.")

    revenue_by_region = df.groupby("region", as_index=False)["revenue"].sum()
    revenue_by_region["revenue"] = revenue_by_region["revenue"].round(2)
    revenue_by_region.to_csv(output_path, index=False)

    return revenue_by_region


if __name__ == "__main__":
    run_pipeline()