from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

file_path = (
    BASE_DIR / "data" / "processed"
    / "transactions_clean.csv"
)

df = pd.read_csv(
    file_path,
    parse_dates=["posting_date", "transaction_date"]
)

print("=" * 55)
print("SPENDWISE SA - DATA VALIDATION")
print("=" * 55)

# ------------------------------------
# 1. Missing balance analysis
# ------------------------------------

missing_balance = df["balance"].isna()

print("\n1. MISSING BALANCES")
print("Rows:", missing_balance.sum())

print("\nCategories of missing balances:")
print(
    df.loc[missing_balance, "category"]
    .value_counts()
    .head(10)
)

# ------------------------------------
# 2. Money in / money out patterns
# ------------------------------------

print("\n2. TRANSACTION AMOUNT PATTERNS")

both_missing = (
    df["money_in"].isna()
    & df["money_out"].isna()
)

both_present = (
    df["money_in"].notna()
    & df["money_out"].notna()
)

only_in = (
    df["money_in"].notna()
    & df["money_out"].isna()
)

only_out = (
    df["money_in"].isna()
    & df["money_out"].notna()
)

print("Only Money In:", only_in.sum())
print("Only Money Out:", only_out.sum())
print("Both populated:", both_present.sum())
print("Both missing:", both_missing.sum())

# ------------------------------------
# 3. Fee patterns
# ------------------------------------

print("\n3. FEE ANALYSIS")

print("Transactions with fees:", df["fee"].notna().sum())

print(
    "Fees with Money Out:",
    (df["fee"].notna() & df["money_out"].notna()).sum()
)

print(
    "Fees without Money Out:",
    (df["fee"].notna() & df["money_out"].isna()).sum()
)

# ------------------------------------
# 4. Transaction categories
# ------------------------------------

print("\n4. CATEGORY COVERAGE")

print("Parent categories:", df["parent_category"].nunique())
print("Categories:", df["category"].nunique())

print(
    "Uncategorized transactions:",
    df["category"].eq("Uncategorized").sum()
)

# ------------------------------------
# 5. Date validation
# ------------------------------------

print("\n5. DATE CHECKS")

print(
    "Posting dates before transaction dates:",
    (df["posting_date"] < df["transaction_date"]).sum()
)

print(
    "Transactions by year:"
)

print(
    df["transaction_date"]
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nValidation completed!")