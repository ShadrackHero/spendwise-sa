from pathlib import Path
import pandas as pd

# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Location of bank statements
RAW_DIR = BASE_DIR / "data" / "raw"

# Find CSV files
csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV file found!")

# Select the first CSV file
file_path = csv_files[0]

# Read CSV
df = pd.read_csv(file_path, sep=None, engine="python")

print("=" * 50)
print("SPENDWISE SA - DATA INSPECTION")
print("=" * 50)

# Dataset dimensions
print("\nDataset Shape:")
print(df.shape)

# Column names
print("\nColumn Names:")

for index, column in enumerate(df.columns, start=1):
    print(f"{index}. {column}")

# Data types
print("\nData Types:")
print(df.dtypes)

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

print("\nInspection completed successfully!")