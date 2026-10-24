from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

df = pd.read_csv(
    BASE_DIR / "data/processed/transactions_clean.csv",
    parse_dates=["posting_date", "transaction_date"]
)

print("=" * 55)
print("SPENDWISE SA - TRANSACTION DIAGNOSTICS")
print("=" * 55)

# 1. Transactions with neither incoming nor outgoing amounts
both_missing = (
    df["money_in"].isna()
    & df["money_out"].isna()
)

subset = df.loc[both_missing]

print("\n1. BOTH AMOUNTS MISSING")
print("Total:", len(subset))
print("With fee:", subset["fee"].notna().sum())
print("Without fee:", subset["fee"].isna().sum())

print("\nCategories:")
print(subset["category"].value_counts().head(15))

print("\nMissing balances among these rows:")
print(subset["balance"].isna().sum())

# 2. Fee-only records
fee_only = (
    both_missing
    & df["fee"].notna()
)

print("\n2. FEE-ONLY RECORDS")
print("Count:", fee_only.sum())

# 3. Date differences
# Compare calendar dates, ignoring time-of-day
posting = df["posting_date"].dt.normalize()
transaction = df["transaction_date"].dt.normalize()

date_difference = (
    posting - transaction
).dt.days

print("\n3. DATE DIFFERENCES")
print("Posting earlier:", (date_difference < 0).sum())
print("Same day:", (date_difference == 0).sum())
print("Posting later:", (date_difference > 0).sum())

print("\nDate difference distribution:")
print(date_difference.value_counts().sort_index().head(20))

print("\nDiagnostics completed!")