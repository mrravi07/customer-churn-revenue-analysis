# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# LEAKAGE-FREE ML DATASET PREPARATION
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
# 02. ANALYSIS WINDOWS
# ============================================================

CUTOFF_DATE = "2026-03-31"

PREDICTION_START = "2026-04-01"

PREDICTION_END = "2026-06-30"


# ============================================================
# 03. BUILD LEAKAGE-FREE DATASET
# ============================================================

query = f"""

WITH eligible_customers AS (

    SELECT
        c.customer_id,
        c.first_name,
        c.age,
        c.gender,
        c.city,
        c.state,
        c.signup_date,
        c.acquisition_channel,
        c.customer_segment,

        s.plan,
        s.contract_type,
        s.monthly_charges,
        s.discount_pct,
        s.payment_method,
        s.auto_renewal

    FROM dim_customer c

    LEFT JOIN dim_subscription s
        ON c.customer_id = s.customer_id

    WHERE c.signup_date::date <= DATE '{CUTOFF_DATE}'
),


activity_features AS (

    SELECT
        customer_id,

        COUNT(*) AS activity_months,

        ROUND(
            AVG(login_count)::numeric,
            2
        ) AS avg_monthly_logins,

        ROUND(
            AVG(session_count)::numeric,
            2
        ) AS avg_monthly_sessions,

        ROUND(
            AVG(avg_session_minutes)::numeric,
            2
        ) AS avg_session_minutes,

        ROUND(
            AVG(features_used)::numeric,
            2
        ) AS avg_features_used,

        ROUND(
            AVG(engagement_score)::numeric,
            2
        ) AS avg_engagement_score,

        MAX(activity_date)::date AS last_activity_date

    FROM fact_customer_activity

    WHERE activity_date::date <= DATE '{CUTOFF_DATE}'

    GROUP BY customer_id
),


revenue_features AS (

    SELECT
        customer_id,

        SUM(
            CASE
                WHEN transaction_type = 'Payment'
                 AND payment_status = 'Success'
                THEN amount
                ELSE 0
            END
        ) AS total_payments,

        SUM(
            CASE
                WHEN transaction_type = 'Refund'
                 AND payment_status = 'Success'
                THEN amount
                ELSE 0
            END
        ) AS total_refunds,

        SUM(
            CASE
                WHEN transaction_type = 'Payment'
                 AND payment_status = 'Success'
                THEN amount

                WHEN transaction_type = 'Refund'
                 AND payment_status = 'Success'
                THEN -amount

                ELSE 0
            END
        ) AS net_revenue,

        COUNT(*) FILTER (
            WHERE transaction_type = 'Payment'
              AND payment_status = 'Success'
        ) AS successful_payments,

        COUNT(*) FILTER (
            WHERE payment_status = 'Failed'
        ) AS failed_payments

    FROM fact_transactions

    WHERE transaction_date::date <= DATE '{CUTOFF_DATE}'

    GROUP BY customer_id
),


support_features AS (

    SELECT
        customer_id,

        COUNT(*) AS total_support_tickets,

        ROUND(
            AVG(satisfaction_score)::numeric,
            2
        ) AS avg_satisfaction_score,

        ROUND(
            AVG(resolution_hours)::numeric,
            2
        ) AS avg_resolution_hours,

        SUM(
            CASE
                WHEN priority = 'High'
                THEN 1
                ELSE 0
            END
        ) AS high_priority_tickets

    FROM fact_support

    WHERE ticket_date::date <= DATE '{CUTOFF_DATE}'

    GROUP BY customer_id
),


future_churn AS (

    SELECT DISTINCT
        customer_id,

        1 AS churn_flag

    FROM fact_churn

    WHERE churn_flag = 1

      AND churn_date::date
          BETWEEN DATE '{PREDICTION_START}'
          AND DATE '{PREDICTION_END}'
)


SELECT

    e.customer_id,
    e.first_name,
    e.age,
    e.gender,
    e.city,
    e.state,
    e.signup_date::date AS signup_date,
    e.acquisition_channel,
    e.customer_segment,

    e.plan,
    e.contract_type,
    e.monthly_charges,
    e.discount_pct,
    e.payment_method,
    e.auto_renewal,

    ROUND(
        (
            DATE '{CUTOFF_DATE}'
            - e.signup_date::date
        ) / 30.44,
        1
    ) AS tenure_months,

    COALESCE(
        a.activity_months,
        0
    ) AS activity_months,

    COALESCE(
        a.avg_monthly_logins,
        0
    ) AS avg_monthly_logins,

    COALESCE(
        a.avg_monthly_sessions,
        0
    ) AS avg_monthly_sessions,

    COALESCE(
        a.avg_session_minutes,
        0
    ) AS avg_session_minutes,

    COALESCE(
        a.avg_features_used,
        0
    ) AS avg_features_used,

    COALESCE(
        a.avg_engagement_score,
        0
    ) AS avg_engagement_score,

    a.last_activity_date,

    COALESCE(
        r.total_payments,
        0
    ) AS total_payments,

    COALESCE(
        r.total_refunds,
        0
    ) AS total_refunds,

    COALESCE(
        r.net_revenue,
        0
    ) AS net_revenue,

    COALESCE(
        r.successful_payments,
        0
    ) AS successful_payments,

    COALESCE(
        r.failed_payments,
        0
    ) AS failed_payments,

    COALESCE(
        sm.total_support_tickets,
        0
    ) AS total_support_tickets,

    COALESCE(
        sm.avg_satisfaction_score,
        0
    ) AS avg_satisfaction_score,

    COALESCE(
        sm.avg_resolution_hours,
        0
    ) AS avg_resolution_hours,

    COALESCE(
        sm.high_priority_tickets,
        0
    ) AS high_priority_tickets,

    COALESCE(
        fc.churn_flag,
        0
    ) AS churn_flag

FROM eligible_customers e

LEFT JOIN activity_features a
    ON e.customer_id = a.customer_id

LEFT JOIN revenue_features r
    ON e.customer_id = r.customer_id

LEFT JOIN support_features sm
    ON e.customer_id = sm.customer_id

LEFT JOIN future_churn fc
    ON e.customer_id = fc.customer_id

ORDER BY e.customer_id;

"""


# ============================================================
# 04. EXECUTE QUERY
# ============================================================

print("\nCreating leakage-free ML dataset...")

df = pd.read_sql(query, engine)

print(f"Rows created    : {len(df):,}")
print(f"Columns created : {len(df.columns)}")


# ============================================================
# 05. TARGET DISTRIBUTION
# ============================================================

print("\nTarget Distribution:")
print(
    df["churn_flag"].value_counts()
)

print("\nTarget Percentage:")
print(
    df["churn_flag"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 06. LEAKAGE CHECK
# ============================================================

forbidden_columns = [
    "churn_date",
    "churn_reason",
    "cancellation_channel"
]

remaining_leakage = [
    col
    for col in forbidden_columns
    if col in df.columns
]

print("\nLeakage Check:")

if remaining_leakage:
    print(
        "WARNING - Leakage columns found:",
        remaining_leakage
    )
else:
    print(
        "PASS - No post-churn columns present."
    )


# ============================================================
# 07. SAVE DATASET
# ============================================================

output_path = "data/ml_dataset.csv"

df.to_csv(
    output_path,
    index=False
)

print(
    f"\nDataset saved to: {output_path}"
)


# ============================================================
# 08. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("LEAKAGE-FREE ML DATASET CREATED")
print("=" * 60)

print(f"Cutoff Date       : {CUTOFF_DATE}")
print(f"Prediction Start  : {PREDICTION_START}")
print(f"Prediction End    : {PREDICTION_END}")
print(f"Rows              : {len(df):,}")
print(f"Columns           : {len(df.columns)}")

print("=" * 60)


