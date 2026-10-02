import os
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

CLEAN_DIR = "data/cleaned"

FILES = {
    "customers": "customers_cleaned.csv",
    "subscriptions": "subscriptions_cleaned.csv",
    "activity": "customer_activity_cleaned.csv",
    "transactions": "transactions_cleaned.csv",
    "support": "support_tickets_cleaned.csv",
    "churn": "churn_cleaned.csv"
}


# ============================================================
# LOAD DATA
# ============================================================

data = {}

for name, filename in FILES.items():

    path = os.path.join(CLEAN_DIR, filename)

    data[name] = pd.read_csv(path)

    print(
        f"Loaded {name:15} → "
        f"{len(data[name]):,} rows"
    )


# ============================================================
# VALIDATION FRAMEWORK
# ============================================================

results = []


def check(table, check_name, condition, message):

    passed = bool(condition)

    results.append({
        "table": table,
        "check": check_name,
        "status": "PASS" if passed else "FAIL",
        "details": message
    })


# ============================================================
# 1. CUSTOMER VALIDATION
# ============================================================

customers = data["customers"]

# Customer ID must be unique
check(
    "customers",
    "Unique Customer IDs",
    customers["customer_id"].is_unique,
    f"Unique IDs: {customers['customer_id'].nunique():,}"
)

# Customer ID cannot be null
check(
    "customers",
    "Customer ID Not Null",
    customers["customer_id"].notna().all(),
    f"Null IDs: {customers['customer_id'].isna().sum():,}"
)

# Age validation
check(
    "customers",
    "Valid Age",
    customers["age"].between(18, 100).all(),
    f"Invalid ages: "
    f"{(~customers['age'].between(18, 100)).sum():,}"
)

# Signup date validation
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"],
    errors="coerce"
)

check(
    "customers",
    "Valid Signup Dates",
    customers["signup_date"].notna().all(),
    f"Invalid dates: {customers['signup_date'].isna().sum():,}"
)


# ============================================================
# 2. SUBSCRIPTION VALIDATION
# ============================================================

subscriptions = data["subscriptions"]

# One subscription per customer
check(
    "subscriptions",
    "Unique Customer Subscription",
    subscriptions["customer_id"].is_unique,
    f"Duplicate customers: "
    f"{subscriptions['customer_id'].duplicated().sum():,}"
)

# Valid plans
valid_plans = {
    "Basic",
    "Standard",
    "Premium",
    "Enterprise"
}

invalid_plans = ~subscriptions["plan"].isin(valid_plans)

check(
    "subscriptions",
    "Valid Subscription Plans",
    (~invalid_plans).all(),
    f"Invalid plans: {invalid_plans.sum():,}"
)

# Positive monthly charges
check(
    "subscriptions",
    "Positive Monthly Charges",
    (subscriptions["monthly_charges"] > 0).all(),
    f"Invalid charges: "
    f"{(subscriptions['monthly_charges'] <= 0).sum():,}"
)


# ============================================================
# 3. ACTIVITY VALIDATION
# ============================================================

activity = data["activity"]

numeric_activity = [
    "login_count",
    "session_count",
    "avg_session_minutes",
    "features_used",
    "engagement_score"
]

for column in numeric_activity:

    check(
        "activity",
        f"Non-negative {column}",
        (activity[column] >= 0).all(),
        f"Invalid values: "
        f"{(activity[column] < 0).sum():,}"
    )


# Engagement score range
check(
    "activity",
    "Engagement Score 0-100",
    activity["engagement_score"].between(0, 100).all(),
    f"Out of range: "
    f"{(~activity['engagement_score'].between(0, 100)).sum():,}"
)


# ============================================================
# 4. TRANSACTION VALIDATION
# ============================================================

transactions = data["transactions"]

# Transaction ID unique
check(
    "transactions",
    "Unique Transaction IDs",
    transactions["transaction_id"].is_unique,
    f"Duplicates: "
    f"{transactions['transaction_id'].duplicated().sum():,}"
)

# Positive amounts
check(
    "transactions",
    "Positive Transaction Amount",
    (transactions["amount"] > 0).all(),
    f"Invalid amounts: "
    f"{(transactions['amount'] <= 0).sum():,}"
)

# Valid transaction types
valid_transaction_types = {
    "Payment",
    "Refund"
}

invalid_transaction_types = ~transactions[
    "transaction_type"
].isin(valid_transaction_types)

check(
    "transactions",
    "Valid Transaction Types",
    (~invalid_transaction_types).all(),
    f"Invalid types: {invalid_transaction_types.sum():,}"
)


# ============================================================
# 5. SUPPORT VALIDATION
# ============================================================

support = data["support"]

# Satisfaction score
check(
    "support",
    "Valid Satisfaction Score",
    support["satisfaction_score"].between(1, 5).all(),
    f"Invalid scores: "
    f"{(~support['satisfaction_score'].between(1, 5)).sum():,}"
)

# Resolution hours
check(
    "support",
    "Valid Resolution Hours",
    (support["resolution_hours"] >= 0).all(),
    f"Invalid values: "
    f"{(support['resolution_hours'] < 0).sum():,}"
)


# ============================================================
# 6. CHURN VALIDATION
# ============================================================

churn = data["churn"]

# One record per customer
check(
    "churn",
    "Unique Customer Churn Record",
    churn["customer_id"].is_unique,
    f"Duplicates: "
    f"{churn['customer_id'].duplicated().sum():,}"
)

# Churn flag
check(
    "churn",
    "Valid Churn Flag",
    churn["churn_flag"].isin([0, 1]).all(),
    f"Invalid flags: "
    f"{(~churn['churn_flag'].isin([0, 1])).sum():,}"
)

# Non-churned customers should not have churn date
non_churn_with_date = (
    (churn["churn_flag"] == 0)
    & churn["churn_date"].notna()
)

check(
    "churn",
    "Non-Churn Customers Have No Churn Date",
    (~non_churn_with_date).all(),
    f"Violations: {non_churn_with_date.sum():,}"
)


# ============================================================
# 7. REFERENTIAL INTEGRITY
# ============================================================

customer_ids = set(
    customers["customer_id"]
)

for table_name, df in data.items():

    if (
        table_name != "customers"
        and "customer_id" in df.columns
    ):

        orphan_records = (
            ~df["customer_id"].isin(customer_ids)
        ).sum()

        check(
            table_name,
            "Referential Integrity",
            orphan_records == 0,
            f"Orphan records: {orphan_records:,}"
        )


# ============================================================
# 8. NULL AUDIT
# ============================================================

for table_name, df in data.items():

    total_nulls = int(
        df.isnull().sum().sum()
    )

    # Nulls are allowed in certain business fields,
    # so this is informational rather than a hard failure.

    results.append({
        "table": table_name,
        "check": "NULL Audit",
        "status": "INFO",
        "details": f"Total NULL cells: {total_nulls:,}"
    })


# ============================================================
# 9. GENERATE VALIDATION REPORT
# ============================================================

validation_report = pd.DataFrame(results)

print("\n" + "=" * 80)
print("DATA VALIDATION REPORT")
print("=" * 80)

print(
    validation_report[
        [
            "table",
            "check",
            "status",
            "details"
        ]
    ].to_string(index=False)
)


# ============================================================
# 10. SAVE REPORT
# ============================================================

REPORT_DIR = "reports"

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)

report_path = os.path.join(
    REPORT_DIR,
    "data_validation_report.csv"
)

validation_report.to_csv(
    report_path,
    index=False
)

print("\nReport saved →", report_path)


# ============================================================
# FINAL STATUS
# ============================================================

failed_checks = (
    validation_report["status"] == "FAIL"
).sum()

passed_checks = (
    validation_report["status"] == "PASS"
).sum()

print("\n" + "=" * 80)
print("FINAL VALIDATION STATUS")
print("=" * 80)

print(f"Passed checks : {passed_checks}")
print(f"Failed checks : {failed_checks}")

if failed_checks == 0:
    print("\n✅ DATASET IS READY FOR ANALYSIS")
else:
    print(
        "\n⚠️ DATASET HAS VALIDATION ISSUES"
    )