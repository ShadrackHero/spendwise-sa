
from pathlib import Path
import pandas as pd

from connection import get_connection

# ----------------------------------------
# 1. Locate categorized transactions
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "transactions_categorized.csv"
)

# ----------------------------------------
# 2. Read unique SpendWise categories
# ----------------------------------------

df = pd.read_csv(INPUT_FILE)

categories = sorted(
    df["spendwise_category"]
    .dropna()
    .unique()
    .tolist()
)

print("=" * 50)
print("SPENDWISE SA - LOAD CATEGORIES")
print("=" * 50)

print("Categories found:", len(categories))

# ----------------------------------------
# 3. Insert categories into PostgreSQL
# ----------------------------------------

with get_connection() as conn:
    with conn.cursor() as cursor:

        for category in categories:
            cursor.execute(
                """
                INSERT INTO categories (category_name)
                VALUES (%s)
                ON CONFLICT (category_name) DO NOTHING;
                """,
                (category,)
            )

        cursor.execute(
            "SELECT COUNT(*) FROM categories;"
        )

        total = cursor.fetchone()[0]

print("Categories in PostgreSQL:", total)
print("Category import completed successfully!")