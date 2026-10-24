from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "transactions_classified.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 55)
print("SPENDWISE SA - CATEGORY ANALYSIS")
print("=" * 55)

# ----------------------------------------
# 1. Parent category summary
# ----------------------------------------

print("\n1. PARENT CATEGORY COUNTS")

parent_summary = (
    df.groupby("parent_category", dropna=False)
    .size()
    .sort_values(ascending=False)
)

print(parent_summary.to_string())

# ----------------------------------------
# 2. Category coverage
# ----------------------------------------

print("\n2. CATEGORY COVERAGE")

print(
    "Unique parent categories:",
    df["parent_category"].nunique()
)

print(
    "Unique categories:",
    df["category"].nunique()
)

print(
    "Uncategorized records:",
    df["category"].eq("Uncategorized").sum()
)

# ----------------------------------------
# 3. Categories by transaction type
# ----------------------------------------

print("\n3. CATEGORY VS TRANSACTION TYPE")

type_summary = pd.crosstab(
    df["parent_category"],
    df["transaction_type"]
)

print(type_summary.to_string())

# ----------------------------------------
# 4. Category mapping combinations
# ----------------------------------------

print("\n4. PARENT/CATEGORY COMBINATIONS")

category_mapping = (
    df[["parent_category", "category"]]
    .drop_duplicates()
    .sort_values(["parent_category", "category"])
)

print(category_mapping.to_string(index=False))

print("\nCategory analysis completed!")