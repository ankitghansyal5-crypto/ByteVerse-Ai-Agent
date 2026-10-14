import pandas as pd
import numpy as np

np.random.seed(42)

# Dataset 1: store sales
n = 300
sales = pd.DataFrame({
    "date": pd.date_range("2025-01-01", periods=n, freq="D"),
    "region": np.random.choice(["North", "South", "East", "West"], n),
    "product": np.random.choice(["Laptop", "Phone", "Tablet", "Headphones"], n),
    "units": np.random.randint(1, 20, n),
    "price": np.random.choice([900, 600, 400, 100], n),
    "customer_status": np.random.choice(["active", "cancelled", "trial"], n),
})
sales["revenue"] = sales["units"] * sales["price"]
sales.loc[5, "units"] = 400          # a planted outlier
sales.loc[10:14, "region"] = None    # some missing values
sales.to_csv("sales.csv", index=False)

# Dataset 2: students (different columns on purpose)
m = 200
students = pd.DataFrame({
    "student_id": range(1, m + 1),
    "branch": np.random.choice(["CSE", "ECE", "Mech", "Civil"], m),
    "study_hours": np.random.randint(1, 10, m),
    "attendance": np.random.randint(50, 100, m),
})
students["marks"] = (students["study_hours"] * 4 + students["attendance"] * 0.4
                     + np.random.randint(-10, 10, m)).round()
students.to_csv("students.csv", index=False)

print("Created sales.csv and students.csv")