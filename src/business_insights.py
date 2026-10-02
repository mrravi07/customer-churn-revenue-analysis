# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# BUSINESS INSIGHTS
# ============================================================

import pandas as pd
from sqlalchemy import create_engine


# ============================================================
# 01. DATABASE CONNECTION
# ============================================================

DB_USER = "postgres"
DB_PASSWORD = "12345"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "customer_churn_db"

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# ============================================================
# 02. LOAD CUSTOMER 360
# ============================================================

print("\nLoading customer_360...")

df = pd.read_sql(
    "SELECT * FROM customer_360;",
    engine
)

print(f"Customers loaded: {len(df):,}")


# ============================================================
# 03. OVERALL BUSINESS KPIs
# ============================================================

total_customers = len(df)

churned_customers = (
    df["churn_flag"] == 1
).sum()

retained_customers = (
    df["churn_flag"] == 0
).sum()

churn_rate = (
    churned_customers
    / total_customers
    * 100
)

total_revenue = df["net_revenue"].sum()

churned_revenue = df.loc[
    df["churn_flag"] == 1,
    "net_revenue"
].sum()

revenue_share_churned = (
    churned_revenue
    / total_revenue
    * 100
)


print("\n" + "=" * 70)
print("OVERALL BUSINESS KPIs")
print("=" * 70)

print(f"Total Customers       : {total_customers:,}")
print(f"Churned Customers     : {churned_customers:,}")
print(f"Retained Customers    : {retained_customers:,}")
print(f"Churn Rate            : {churn_rate:.2f}%")
print(f"Total Net Revenue     : ₹{total_revenue:,.2f}")
print(f"Churned Customer Rev. : ₹{churned_revenue:,.2f}")
print(
    f"Churned Revenue Share : "
    f"{revenue_share_churned:.2f}%"
)


# ============================================================
# 04. CHURN BY CONTRACT TYPE
# ============================================================

print("\n" + "=" * 70)
print("CHURN BY CONTRACT TYPE")
print("=" * 70)

contract_analysis = (
    df.groupby("contract_type")
    .agg(
        total_customers=("customer_id", "count"),
        churned_customers=("churn_flag", "sum"),
        avg_revenue=("net_revenue", "mean")
    )
    .reset_index()
)

contract_analysis["churn_rate_pct"] = (
    contract_analysis["churned_customers"]
    / contract_analysis["total_customers"]
    * 100
)

print(
    contract_analysis[
        [
            "contract_type",
            "total_customers",
            "churned_customers",
            "churn_rate_pct",
            "avg_revenue"
        ]
    ]
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 05. CHURN BY ENGAGEMENT
# ============================================================

print("\n" + "=" * 70)
print("CHURN BY ENGAGEMENT LEVEL")
print("=" * 70)


def engagement_group(score):

    if score <= 20:
        return "Very Low"

    elif score <= 40:
        return "Low"

    elif score <= 60:
        return "Moderate"

    elif score <= 80:
        return "High"

    else:
        return "Very High"


df["engagement_group"] = (
    df["avg_engagement_score"]
    .apply(engagement_group)
)


engagement_analysis = (
    df.groupby("engagement_group")
    .agg(
        total_customers=("customer_id", "count"),
        churned_customers=("churn_flag", "sum"),
        avg_engagement=("avg_engagement_score", "mean"),
        avg_revenue=("net_revenue", "mean")
    )
    .reset_index()
)

engagement_analysis["churn_rate_pct"] = (
    engagement_analysis["churned_customers"]
    / engagement_analysis["total_customers"]
    * 100
)

print(
    engagement_analysis[
        [
            "engagement_group",
            "total_customers",
            "churned_customers",
            "churn_rate_pct",
            "avg_engagement",
            "avg_revenue"
        ]
    ]
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 06. CHURN BY FAILED PAYMENTS
# ============================================================

print("\n" + "=" * 70)
print("CHURN BY FAILED PAYMENTS")
print("=" * 70)


def failed_payment_group(count):

    if count == 0:
        return "0 Failed Payments"

    elif count <= 2:
        return "1-2 Failed Payments"

    elif count <= 5:
        return "3-5 Failed Payments"

    else:
        return "6+ Failed Payments"


df["failed_payment_group"] = (
    df["failed_payments"]
    .apply(failed_payment_group)
)


payment_analysis = (
    df.groupby("failed_payment_group")
    .agg(
        total_customers=("customer_id", "count"),
        churned_customers=("churn_flag", "sum"),
        avg_revenue=("net_revenue", "mean")
    )
    .reset_index()
)

payment_analysis["churn_rate_pct"] = (
    payment_analysis["churned_customers"]
    / payment_analysis["total_customers"]
    * 100
)

print(
    payment_analysis[
        [
            "failed_payment_group",
            "total_customers",
            "churned_customers",
            "churn_rate_pct",
            "avg_revenue"
        ]
    ]
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 07. CHURN BY SUPPORT SATISFACTION
# ============================================================

print("\n" + "=" * 70)
print("CHURN BY SUPPORT SATISFACTION")
print("=" * 70)


def satisfaction_group(score):

    if score == 0:
        return "No Support Rating"

    elif score < 2:
        return "Very Low (1-2)"

    elif score < 3:
        return "Low (2-3)"

    elif score < 4:
        return "Moderate (3-4)"

    else:
        return "High (4-5)"


df["satisfaction_group"] = (
    df["avg_satisfaction_score"]
    .apply(satisfaction_group)
)


support_analysis = (
    df.groupby("satisfaction_group")
    .agg(
        total_customers=("customer_id", "count"),
        churned_customers=("churn_flag", "sum"),
        avg_resolution_hours=("avg_resolution_hours", "mean")
    )
    .reset_index()
)

support_analysis["churn_rate_pct"] = (
    support_analysis["churned_customers"]
    / support_analysis["total_customers"]
    * 100
)

print(
    support_analysis[
        [
            "satisfaction_group",
            "total_customers",
            "churned_customers",
            "churn_rate_pct",
            "avg_resolution_hours"
        ]
    ]
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 08. HIGH-VALUE CHURNED CUSTOMERS
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 HIGH-VALUE CHURNED CUSTOMERS")
print("=" * 70)

high_value_churn = (
    df[df["churn_flag"] == 1]
    [
        [
            "customer_id",
            "customer_segment",
            "plan",
            "contract_type",
            "monthly_charges",
            "tenure_months",
            "avg_engagement_score",
            "failed_payments",
            "net_revenue"
        ]
    ]
    .sort_values(
        "net_revenue",
        ascending=False
    )
    .head(20)
)

print(
    high_value_churn
    .round(2)
    .to_string(index=False)
)


# ============================================================
# 09. BUSINESS RISK PROFILE
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS RISK PROFILE")
print("=" * 70)

high_risk_profile = df[
    (
        (df["contract_type"] == "Monthly")
        |
        (df["avg_engagement_score"] < 40)
        |
        (df["failed_payments"] >= 3)
        |
        (
            (df["avg_satisfaction_score"] > 0)
            &
            (df["avg_satisfaction_score"] < 3)
        )
    )
]

print(
    f"Customers matching at least one "
    f"risk signal : {len(high_risk_profile):,}"
)

print(
    f"Churned among them : "
    f"{high_risk_profile['churn_flag'].sum():,}"
)

print(
    f"Churn rate among them : "
    f"{high_risk_profile['churn_flag'].mean() * 100:.2f}%"
)

print(
    f"Associated revenue : "
    f"₹{high_risk_profile['net_revenue'].sum():,.2f}"
)


# ============================================================
# 10. SAVE BUSINESS SUMMARY
# ============================================================

summary = pd.DataFrame({
    "metric": [
        "Total Customers",
        "Churned Customers",
        "Retained Customers",
        "Churn Rate %",
        "Total Net Revenue",
        "Churned Customer Revenue",
        "Churned Revenue Share %"
    ],
    "value": [
        total_customers,
        churned_customers,
        retained_customers,
        round(churn_rate, 2),
        round(total_revenue, 2),
        round(churned_revenue, 2),
        round(revenue_share_churned, 2)
    ]
})

summary.to_csv(
    "data/business_summary.csv",
    index=False
)

print(
    "\nSaved: data/business_summary.csv"
)


# ============================================================
# 11. COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("BUSINESS INSIGHTS ANALYSIS COMPLETED")
print("=" * 70)