from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data/processed/transactions_classified.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data/processed/category_mapping.csv"
)

df = pd.read_csv(INPUT_FILE)

# Preserve the original parent categories
parents = sorted(
    df["parent_category"].dropna().unique()
)

mapping = {
    "Account Payment Received": ("Other Receipts", "Review"),
    "Allowance": ("Family Support", "Expense"),
    "Cash": ("Cash Withdrawals", "Transfer / Review"),
    "Cash Deposit": ("Cash Deposits", "Review"),
    "Communication": ("Phone & Internet", "Expense"),
    "Education": ("Education", "Expense"),
    "Entertainment": ("Entertainment", "Expense"),
    "Fees": ("Banking Charges", "Expense"),
    "Food": ("Food & Dining", "Expense"),
    "Household": ("Housing & Utilities", "Expense"),
    "Insurance": ("Insurance", "Expense"),
    "Interest": ("Interest Income", "Income"),
    "Loans & Accounts": ("Debt Payments", "Transfer / Review"),
    "Other Income": ("Other Receipts", "Review"),
    "Payment Received": ("Other Receipts", "Review"),
    "Personal & Family": ("Personal & Family", "Expense"),
    "Refunds": ("Refunds", "Review"),
    "Rental Income": ("Rental Income", "Review"),
    "Salary": ("Employment Income", "Review"),
    "Transfer": ("Transfers", "Transfer / Review"),
    "Transport": ("Transport", "Expense"),
    "Uncategorised": ("Uncategorized", "Review"),
    "Uncategorized": ("Uncategorized", "Review"),
}

rows = []

for parent in parents:
    category, cash_flow_class = mapping.get(
        parent,
        ("Uncategorized", "Review")
    )

    rows.append({
        "parent_category": parent,
        "spendwise_category": category,
        "cash_flow_class": cash_flow_class
    })

mapping_df = pd.DataFrame(rows)

mapping_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 55)
print("SPENDWISE SA - CATEGORY MAPPING")
print("=" * 55)

print("\nMapping rows:", len(mapping_df))
print("\nCash-flow classifications:")
print(mapping_df["cash_flow_class"].value_counts())

print("\nMapping created successfully!")