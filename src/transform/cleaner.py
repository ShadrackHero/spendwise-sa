from pathlib import Path
import pandas as pd

# ---------------------------------------
# 1. Define project paths
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(RAW_DIR.glob("*.csv"))

if len(csv_files) != 1:
    raise ValueError(
        f"Expected exactly one CSV in data/raw, "
        f"found {len(csv_files)}."
    )

file_path = csv_files[0]

# ---------------------------------------
# 2. Load original dataset
# ---------------------------------------

df = pd.read_csv(file_path)

print("=" * 55)
print("SPENDWISE SA - DATA CLEANING")
print("=" * 55)

print("\nOriginal shape:", df.shape)

# ---------------------------------------
# 3. Standardize column names
# ---------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

# ---------------------------------------
# 4. Convert date columns
# ---------------------------------------

date_columns = [
    "posting_date",
    "transaction_date"
]

for col in date_columns:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce",
        dayfirst=True
    )

# ---------------------------------------
# 5. Clean text columns
# ---------------------------------------

text_columns = [
    "description",
    "original_description",
    "parent_category",
    "category"
]

for col in text_columns:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# Fill only missing category labels
df["parent_category"] = (
    df["parent_category"].fillna("Uncategorized")
)

df["category"] = (
    df["category"].fillna("Uncategorized")
)

# ---------------------------------------
# 6. Convert numeric columns
# ---------------------------------------

numeric_columns = [
    "money_in",
    "money_out",
    "fee",
    "balance"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ---------------------------------------
# 7. Data quality checks
# ---------------------------------------

print("\nMissing values after cleaning:")
print(df.isna().sum())

print("\nInvalid posting dates:")
print(df["posting_date"].isna().sum())

print("\nInvalid transaction dates:")
print(df["transaction_date"].isna().sum())

print("\nDuplicate Nr values:")
print(df["nr"].duplicated().sum())

print("\nFully duplicated rows:")
print(df.duplicated().sum())

# ---------------------------------------
# 8. Date coverage
# ---------------------------------------

print("\nTransaction date coverage:")

print("Start:", df["transaction_date"].min())
print("End:", df["transaction_date"].max())

# ---------------------------------------
# 9. Save cleaned dataset
# ---------------------------------------

output_file = (
    PROCESSED_DIR / "transactions_clean.csv"
)

df.to_csv(output_file, index=False)

print("\nCleaned dataset saved locally.")
print("Final shape:", df.shape)

print("\nCleaning completed successfully!")