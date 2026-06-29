import pandas as pd

# Load dataset
df = pd.read_csv(
    "data/combinenew.csv",
    low_memory=False
)

# Show first rows
print("\n===== FIRST 5 ROWS =====")
print(df.head())

# Show columns
print("\n===== COLUMNS =====")
print(df.columns)

# Dataset size
print("\n===== DATASET SHAPE =====")
print(df.shape)

# Null values
print("\n===== NULL VALUES =====")
print(df.isnull().sum())