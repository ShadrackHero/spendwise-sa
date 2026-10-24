from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data/processed"

transactions = pd.read_csv(
    PROCESSED_DIR / "transactions_classified.csv"
)

mapping = pd.read_csv(
    PROCESSED_DIR / "category_mapping.csv"
)

# Ensure each parent category has one mapping
if mapping["parent_category"].duplicated().any():
    raise ValueError("Duplicate category mapping detected!")

# Merge category rules
df = transactions.merge(
    mapping,
    on="parent_category",
    how="left",
    validate="many_to_one"
)

# Check for unmapped categories
unmapped = df["spendwise_category"].isna()

print("=" * 55)
print("SPENDWISE SA - APPLY CATEGORIES")
print("=" * 55)

print("\nOriginal transactions:", len(transactions))
print("Mapped transactions:", len(df))
print("Unmapped transactions:", unmapped.sum())

if unmapped.any():
    raise ValueError(
        "Some transactions have no category mapping."
    )

print("\nSpendWise categories:")
print(
    df["spendwise_category"]
    .value_counts()
    .to_string()
)

print("\nCash-flow classifications:")
print(
    df["cash_flow_class"]
    .value_counts()
    .to_string()
)

OUTPUT_FILE = (
    PROCESSED_DIR / "transactions_categorized.csv"
)

df.to_csv(OUTPUT_FILE, index=False)

print("\nCategorization completed successfully!")
print("Final shape:", df.shape) 