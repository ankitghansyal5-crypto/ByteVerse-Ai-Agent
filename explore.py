import pandas as pd

df = pd.read_csv("sales.csv")

print("SHAPE (rows, columns):", df.shape)
print()
print("COLUMNS:", list(df.columns))
print()
print("FIRST 5 ROWS:")
print(df.head())
print()
print("MISSING VALUES PER COLUMN:")
print(df.isna().sum())
print()
print("SUMMARY STATS:")
print(df.describe())
print()
print("REVENUE BY REGION:")
print(df.groupby("region")["revenue"].sum().sort_values(ascending=False))