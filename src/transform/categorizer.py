from pathlib import Path
import pandas as pd
import numpy as np

# ----------------------------------------
# 1. File paths
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data/processed/transactions_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data/processed/transactions_classified.csv"
)

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["posting_date", "transaction_date"]
)

# ----------------------------------------
# 2. Identify transaction types
# ----------------------------------------

conditions = [
    df["money_in"].notna(),
    df["money_out"].notna(),
    df["fee"].notna()
]

choices = [
    "Money In",
    "Money Out",
    "Bank Fee"
]

df["transaction_type"] = np.select(
    conditions,
    choices,
    default="Unclassified"
)

# ----------------------------------------
# 3. Standardize transaction amounts
# ----------------------------------------

# Always positive for reporting purposes
df["transaction_amount"] = np.select(
    conditions,
    [
        df["money_in"].abs().fillna(0),
        df["money_out"].abs().fillna(0),
        df["fee"].abs().fillna(0)
    ],
    default=np.nan
)

# ----------------------------------------
# 4. Calculate signed cash flow
# ----------------------------------------

# Preserve original Capitec signs
df["cash_flow"] = np.select(
    conditions,
    [
        df["money_in"].fillna(0),
        df["money_out"].fillna(0),
        df["fee"].fillna(0)
    ],
    default=np.nan
)

# ----------------------------------------
# 5. Posting delay
# ----------------------------------------

df["posting_delay_days"] = (
    df["posting_date"].dt.normalize()
    - df["transaction_date"].dt.normalize()
).dt.days

# ----------------------------------------
# 6. Flag records requiring review
# ----------------------------------------

df["review_required"] = (
    df["transaction_type"].eq("Unclassified")
    | df["posting_delay_days"].lt(0)
)

# ----------------------------------------
# 7. Validate amount signs
# ----------------------------------------

print("=" * 55)
print("SPENDWISE SA - TRANSACTION CLASSIFICATION")
print("=" * 55)

print("\nTransaction types:")
print(df["transaction_type"].value_counts())

print("\nAmount sign validation:")

print(
    "Negative Money In values:",
    df["money_in"].lt(0).sum()
)

print(
    "Positive Money Out values:",
    df["money_out"].gt(0).sum()
)

print(
    "Positive Fee values:",
    df["fee"].gt(0).sum()
)

# ----------------------------------------
# 8. Financial reconciliation
# ----------------------------------------

expected_cash_flow = (
    df["money_in"].sum()
    + df["money_out"].sum()
    + df["fee"].sum()
)

actual_cash_flow = df["cash_flow"].sum()

print("\nFinancial reconciliation:")

print(
    "Net cash flow:",
    round(actual_cash_flow, 2)
)

print(
    "Reconciliation difference:",
    round(actual_cash_flow - expected_cash_flow, 2)
)

# ----------------------------------------
# 9. Data quality summary
# ----------------------------------------

print("\nRecords requiring review:")
print(df["review_required"].sum())

print("\nMissing standardized amounts:")
print(df["transaction_amount"].isna().sum())

# ----------------------------------------
# 10. Save classified dataset
# ----------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("\nClassification completed!")
print("Final shape:", df.shape)