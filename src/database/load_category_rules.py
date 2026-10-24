
from pathlib import Path
import pandas as pd

from connection import get_connection

# ----------------------------------------
# 1. File paths
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data/processed/category_mapping.csv"
)

# ----------------------------------------
# 2. Read category mapping
# ----------------------------------------

df = pd.read_csv(INPUT_FILE, keep_default_na=False)

print("=" * 50)
print("SPENDWISE SA - LOAD CATEGORY RULES")
print("=" * 50)

print("Mapping rules found:", len(df))

# ----------------------------------------
# 3. Validate the mapping
# ----------------------------------------

required_columns = [
    "parent_category",
    "spendwise_category",
    "cash_flow_class"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

if df["parent_category"].duplicated().any():
    raise ValueError(
        "Duplicate parent categories found."
    )

if df[required_columns].eq("").any().any():
    raise ValueError(
        "Blank category mapping values found."
    )

# ----------------------------------------
# 4. Insert rules into PostgreSQL
# ----------------------------------------

with get_connection() as conn:
    with conn.cursor() as cursor:

        for row in df.itertuples(index=False):

            cursor.execute(
                """
                INSERT INTO category_rules (
                    bank_parent_category,
                    category_id,
                    cash_flow_class
                )
                SELECT
                    %s,
                    category_id,
                    %s
                FROM categories
                WHERE category_name = %s
                ON CONFLICT (bank_parent_category)
                DO UPDATE SET
                    category_id = EXCLUDED.category_id,
                    cash_flow_class = EXCLUDED.cash_flow_class;
                """,
                (
                    row.parent_category,
                    row.cash_flow_class,
                    row.spendwise_category
                )
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    "No matching SpendWise category for: "
                    f"{row.parent_category}"
                )

        cursor.execute(
            "SELECT COUNT(*) FROM category_rules;"
        )

        total = cursor.fetchone()[0]

print("Rules in PostgreSQL:", total)
print("Category rules imported successfully!")
