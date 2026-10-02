import os
import pandas as pd
import numpy as np

RAW_DIR = "data/raw"
CLEAN_DIR = "data/cleaned"

os.makedirs(CLEAN_DIR, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def save_cleaned(df, filename):
    path = os.path.join(CLEAN_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Saved → {path} | Rows: {len(df):,}")


# ============================================================
# 1. CUSTOMERS
# ============================================================

print_section("CLEANING CUSTOMERS")

customers = pd.read_csv(
    os.path.join(RAW_DIR, "customers.csv")
)

print("Original rows:", len(customers))

# Remove exact duplicate rows
customers = customers.drop_duplicates()

# Remove duplicate customer IDs
customers = customers.drop_duplicates(
    subset="customer_id",
    keep="first"
)

# Convert date
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="coerce"
)

# Standardize text columns
text_columns = [
    "first_name",
    "gender",
    "city",
    "state",
    "acquisition_channel",
    "customer_segment"
]

for col in text_columns:
    customers[col] = (
        customers[col]
        .astype("string")
        .str.strip()
    )

# Handle missing acquisition channel
customers["acquisition_channel"] = (
    customers["acquisition_channel"]
    .fillna("Unknown")
)

# Validate age
customers.loc[
    (customers["age"] < 18) |
    (customers["age"] > 100),
    "age"
] = np.nan

# Median age imputation
customers["age"] = customers["age"].fillna(
    customers["age"].median()
)

save_cleaned(
    customers,
    "customers_cleaned.csv"
)


# ============================================================
# 2. SUBSCRIPTIONS
# ============================================================

print_section("CLEANING SUBSCRIPTIONS")

subscriptions = pd.read_csv(
    os.path.join(RAW_DIR, "subscriptions.csv")
)

subscriptions = subscriptions.drop_duplicates(
    subset="subscription_id",
    keep="first"
)

subscriptions["subscription_start_date"] = pd.to_datetime(
    subscriptions["subscription_start_date"],
    errors="coerce"
)

subscriptions["plan"] = (
    subscriptions["plan"]
    .astype("string")
    .str.strip()
)

subscriptions["contract_type"] = (
    subscriptions["contract_type"]
    .astype("string")
    .str.strip()
)

subscriptions["payment_method"] = (
    subscriptions["payment_method"]
    .astype("string")
    .str.strip()
)

# Validate charges
subscriptions.loc[
    subscriptions["monthly_charges"] <= 0,
    "monthly_charges"
] = np.nan

subscriptions["monthly_charges"] = (
    subscriptions["monthly_charges"]
    .fillna(
        subscriptions.groupby("plan")[
            "monthly_charges"
        ].transform("median")
    )
)

save_cleaned(
    subscriptions,
    "subscriptions_cleaned.csv"
)


# ============================================================
# 3. CUSTOMER ACTIVITY
# ============================================================

print_section("CLEANING CUSTOMER ACTIVITY")

activity = pd.read_csv(
    os.path.join(RAW_DIR, "customer_activity.csv")
)

activity["activity_date"] = pd.to_datetime(
    activity["activity_date"],
    errors="coerce"
)

numeric_cols = [
    "login_count",
    "session_count",
    "avg_session_minutes",
    "features_used",
    "engagement_score"
]

for col in numeric_cols:
    activity[col] = pd.to_numeric(
        activity[col],
        errors="coerce"
    )

# Remove impossible negative values
for col in numeric_cols:
    activity.loc[
        activity[col] < 0,
        col
    ] = np.nan

# Handle session-duration outliers
upper_limit = activity[
    "avg_session_minutes"
].quantile(0.99)

activity.loc[
    activity["avg_session_minutes"] > upper_limit,
    "avg_session_minutes"
] = upper_limit

# Fill numeric missing values
for col in numeric_cols:
    activity[col] = activity[col].fillna(
        activity[col].median()
    )

# Recalculate engagement score
activity["engagement_score"] = np.clip(
    (
        activity["login_count"] * 2
        + activity["features_used"] * 4
        + activity["avg_session_minutes"]
    ),
    0,
    100
).round(2)

save_cleaned(
    activity,
    "customer_activity_cleaned.csv"
)


# ============================================================
# 4. TRANSACTIONS
# ============================================================

print_section("CLEANING TRANSACTIONS")

transactions = pd.read_csv(
    os.path.join(RAW_DIR, "transactions.csv")
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

transactions["transaction_type"] = (
    transactions["transaction_type"]
    .astype("string")
    .str.strip()
)

transactions["payment_status"] = (
    transactions["payment_status"]
    .astype("string")
    .str.strip()
)

transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
)

# Remove invalid transaction amounts
transactions = transactions[
    transactions["amount"] > 0
].copy()

# Remove duplicate transactions
transactions = transactions.drop_duplicates(
    subset="transaction_id",
    keep="first"
)

save_cleaned(
    transactions,
    "transactions_cleaned.csv"
)


# ============================================================
# 5. SUPPORT TICKETS
# ============================================================

print_section("CLEANING SUPPORT TICKETS")

support = pd.read_csv(
    os.path.join(RAW_DIR, "support_tickets.csv")
)

support["ticket_date"] = pd.to_datetime(
    support["ticket_date"],
    errors="coerce"
)

support["resolution_hours"] = pd.to_numeric(
    support["resolution_hours"],
    errors="coerce"
)

support["satisfaction_score"] = pd.to_numeric(
    support["satisfaction_score"],
    errors="coerce"
)

# Validate satisfaction score
support.loc[
    (support["satisfaction_score"] < 1) |
    (support["satisfaction_score"] > 5),
    "satisfaction_score"
] = np.nan

# Median imputation
support["satisfaction_score"] = (
    support["satisfaction_score"]
    .fillna(
        support["satisfaction_score"].median()
    )
)

# Validate resolution time
support.loc[
    support["resolution_hours"] < 0,
    "resolution_hours"
] = np.nan

support["resolution_hours"] = (
    support["resolution_hours"]
    .fillna(
        support["resolution_hours"].median()
    )
)

support = support.drop_duplicates(
    subset="ticket_id",
    keep="first"
)

save_cleaned(
    support,
    "support_tickets_cleaned.csv"
)


# ============================================================
# 6. CHURN
# ============================================================

print_section("CLEANING CHURN")

churn = pd.read_csv(
    os.path.join(RAW_DIR, "churn.csv")
)

churn["churn_date"] = pd.to_datetime(
    churn["churn_date"],
    errors="coerce"
)

churn["churn_flag"] = pd.to_numeric(
    churn["churn_flag"],
    errors="coerce"
)

# Keep valid churn flags only
churn = churn[
    churn["churn_flag"].isin([0, 1])
].copy()

churn = churn.drop_duplicates(
    subset="customer_id",
    keep="first"
)

# For non-churned customers these should be null
churn.loc[
    churn["churn_flag"] == 0,
    ["churn_date", "churn_reason", "cancellation_channel"]
] = np.nan

save_cleaned(
    churn,
    "churn_cleaned.csv"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print_section("CLEANING COMPLETED")

print("\nCleaned files:")

for filename in os.listdir(CLEAN_DIR):
    print("✓", filename)

print("\nData cleaning pipeline completed successfully.")