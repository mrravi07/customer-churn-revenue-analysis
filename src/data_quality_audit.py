import pandas as pd
import os

DATA_DIR = "data/raw"

FILES = {
    "customers": "customers.csv",
    "subscriptions": "subscriptions.csv",
    "activity": "customer_activity.csv",
    "transactions": "transactions.csv",
    "support": "support_tickets.csv",
    "churn": "churn.csv"
}


# ============================================================
# 1. LOAD DATA
# ============================================================

data = {}

for name, file in FILES.items():
    path = os.path.join(DATA_DIR, file)
    data[name] = pd.read_csv(path)

    print(f"{name:15} → {data[name].shape}")


# ============================================================
# 2. BASIC DATA PROFILE
# ============================================================

print("\n" + "=" * 70)
print("BASIC DATA PROFILE")
print("=" * 70)

for name, df in data.items():

    print(f"\n--- {name.upper()} ---")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    print(list(df.columns))


# ============================================================
# 3. MISSING VALUE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUE AUDIT")
print("=" * 70)

for name, df in data.items():

    missing = df.isnull().sum()

    missing = missing[missing > 0]

    print(f"\n--- {name.upper()} ---")

    if len(missing) == 0:
        print("No missing values found.")
    else:
        print(missing)


# ============================================================
# 4. DUPLICATE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATE AUDIT")
print("=" * 70)

for name, df in data.items():

    duplicates = df.duplicated().sum()

    print(
        f"{name:15} → {duplicates:,} duplicate rows"
    )


# ============================================================
# 5. CUSTOMER ID DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER ID DUPLICATE AUDIT")
print("=" * 70)

for name, df in data.items():

    if "customer_id" in df.columns:

        duplicates = df["customer_id"].duplicated().sum()

        print(
            f"{name:15} → {duplicates:,} duplicate customer IDs"
        )


# ============================================================
# 6. DATA TYPES
# ============================================================

print("\n" + "=" * 70)
print("DATA TYPES")
print("=" * 70)

for name, df in data.items():

    print(f"\n--- {name.upper()} ---")

    print(df.dtypes)


# ============================================================
# 7. NUMERICAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("NUMERICAL SUMMARY")
print("=" * 70)

for name, df in data.items():

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        print(f"\n--- {name.upper()} ---")

        print(
            df[numeric_columns].describe().round(2)
        )


# ============================================================
# 8. CATEGORICAL VALUE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("CATEGORICAL VALUE AUDIT")
print("=" * 70)

for name, df in data.items():

    categorical_columns = df.select_dtypes(
        include="object"
    ).columns

    print(f"\n--- {name.upper()} ---")

    for column in categorical_columns:

        unique_values = df[column].dropna().unique()

        print(
            f"\n{column}: {len(unique_values)} unique values"
        )

        print(unique_values[:15])


# ============================================================
# 9. DATE RANGE AUDIT
# ============================================================

print("\n" + "=" * 70)
print("DATE RANGE AUDIT")
print("=" * 70)

for name, df in data.items():

    date_columns = [
        col for col in df.columns
        if "date" in col.lower()
    ]

    if date_columns:

        print(f"\n--- {name.upper()} ---")

        for column in date_columns:

            dates = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            print(
                f"{column}: "
                f"{dates.min()} → {dates.max()}"
            )


# ============================================================
# 10. BUSINESS RULE CHECKS
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS RULE VALIDATION")
print("=" * 70)


# Age
customers = data["customers"]

invalid_age = (
    (customers["age"] < 18) |
    (customers["age"] > 100)
).sum()

print(
    f"\nInvalid age records: {invalid_age:,}"
)


# Revenue
transactions = data["transactions"]

negative_amounts = (
    transactions["amount"] < 0
).sum()

print(
    f"Negative transaction amounts: "
    f"{negative_amounts:,}"
)


# Subscription charges
subscriptions = data["subscriptions"]

invalid_charges = (
    subscriptions["monthly_charges"] <= 0
).sum()

print(
    f"Invalid monthly charges: "
    f"{invalid_charges:,}"
)


# Satisfaction
support = data["support"]

invalid_satisfaction = (
    (support["satisfaction_score"] < 1) |
    (support["satisfaction_score"] > 5)
).sum()

print(
    f"Invalid satisfaction scores: "
    f"{invalid_satisfaction:,}"
)


# ============================================================
# 11. REFERENTIAL INTEGRITY
# ============================================================

print("\n" + "=" * 70)
print("REFERENTIAL INTEGRITY")
print("=" * 70)

customer_ids = set(
    customers["customer_id"].dropna()
)

for name, df in data.items():

    if (
        name != "customers"
        and "customer_id" in df.columns
    ):

        orphan_records = (
            ~df["customer_id"].isin(customer_ids)
        ).sum()

        print(
            f"{name:15} → "
            f"{orphan_records:,} orphan records"
        )


print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("=" * 70)
