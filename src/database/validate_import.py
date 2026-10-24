
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data/processed/transactions_categorized.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 55)
print("SPENDWISE SA - PRE-IMPORT VALIDATION")
print("=" * 55)

# ----------------------------------------
# 1. Check required columns
# ----------------------------------------

required_columns = [
    "nr",
    "posting_date",
    "transaction_date",
    "description",
    "original_description",
    "parent_category",
    "category",
    "money_in",
    "money_out",
    "fee",
    "balance",
    "transaction_type",
    "transaction_amount",
    "cash_flow",
    "posting_delay_days",
    "review_required",
    "spendwise_category",
    "cash_flow_class"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

print("\nMissing required columns:", missing)

if missing:
    raise ValueError("CSV schema does not match expected columns.")

# ----------------------------------------
# 2. Validate source identifiers
# ----------------------------------------

print("\nTotal records:", len(df))
print("Missing source IDs:", df["nr"].isna().sum())
print("Duplicate source IDs:", df["nr"].duplicated().sum())

# ----------------------------------------
# 3. Validate category mapping
# ----------------------------------------

print("\nMissing SpendWise categories:",
      df["spendwise_category"].isna().sum())

print("Missing cash-flow classes:",
      df["cash_flow_class"].isna().sum())

# ----------------------------------------
# 4. Validate financial fields
# ----------------------------------------

print("\nMissing balances:", df["balance"].isna().sum())

print("Missing transaction amounts:",
      df["transaction_amount"].isna().sum())

print("Missing cash-flow values:",
      df["cash_flow"].isna().sum())

# ----------------------------------------
# 5. Validate review flags
# ----------------------------------------

print("\nReview-required records:",
      df["review_required"].sum())

print("\nTransaction types:")
print(df["transaction_type"].value_counts())

# ----------------------------------------
# 6. Final validation
# ----------------------------------------

assert len(df) == 1464, "Unexpected number of transactions"
assert df["nr"].notna().all(), "Missing transaction IDs"
assert df["nr"].is_unique, "Duplicate transaction IDs"
assert df["spendwise_category"].notna().all(), "Unmapped categories"
assert df["cash_flow_class"].notna().all(), "Missing cash-flow classes"

print("\nPRE-IMPORT VALIDATION PASSED!")
