import os
import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

SEED = 2026

N_CUSTOMERS = 50_000

START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2026-06-30")

OUTPUT_DIR = "data/raw"

rng = np.random.default_rng(SEED)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def make_ids(prefix, n, digits=6):
    return [f"{prefix}{i:0{digits}d}" for i in range(1, n + 1)]


# ============================================================
# 1. CUSTOMER MASTER
# ============================================================

print("\n[1/6] Generating customers...")

customer_ids = make_ids("C", N_CUSTOMERS)

first_names = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rahul",
    "Rohan", "Karan", "Vikram", "Neha", "Priya",
    "Ananya", "Sneha", "Pooja", "Isha", "Simran",
    "Aisha", "Kabir", "Riya", "Nikhil", "Aman"
]

states = [
    "Delhi", "Haryana", "Maharashtra", "Karnataka",
    "Uttar Pradesh", "Bihar", "West Bengal",
    "Tamil Nadu", "Telangana", "Gujarat",
    "Rajasthan", "Punjab"
]

cities = [
    "Delhi", "Gurugram", "Mumbai", "Pune",
    "Bengaluru", "Noida", "Lucknow", "Patna",
    "Kolkata", "Chennai", "Hyderabad", "Ahmedabad",
    "Jaipur", "Chandigarh"
]

channels = [
    "Organic Search",
    "Google Ads",
    "Social Media",
    "Referral",
    "Email Campaign",
    "Partner"
]

segments = ["Consumer", "SMB", "Enterprise"]

# ------------------------------------------------------------
# IMPORTANT:
# Signup dates now extend through June 2026.
# This creates genuine 0–3 month customers.
# ------------------------------------------------------------

signup_days = rng.integers(
    0,
    (END_DATE - START_DATE).days + 1,
    N_CUSTOMERS
)

signup_dates = START_DATE + pd.to_timedelta(
    signup_days,
    unit="D"
)

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "first_name": rng.choice(first_names, N_CUSTOMERS),
    "age": rng.integers(18, 66, N_CUSTOMERS),
    "gender": rng.choice(
        ["Male", "Female", "Other"],
        N_CUSTOMERS,
        p=[0.52, 0.46, 0.02]
    ),
    "city": rng.choice(cities, N_CUSTOMERS),
    "state": rng.choice(states, N_CUSTOMERS),
    "signup_date": signup_dates,
    "acquisition_channel": rng.choice(
        channels,
        N_CUSTOMERS,
        p=[0.20, 0.20, 0.18, 0.15, 0.12, 0.15]
    ),
    "customer_segment": rng.choice(
        segments,
        N_CUSTOMERS,
        p=[0.70, 0.23, 0.07]
    )
})


# ============================================================
# 2. SUBSCRIPTIONS
# ============================================================

print("[2/6] Generating subscriptions...")

plans = rng.choice(
    ["Basic", "Standard", "Premium", "Enterprise"],
    N_CUSTOMERS,
    p=[0.35, 0.40, 0.20, 0.05]
)

plan_prices = {
    "Basic": 399,
    "Standard": 699,
    "Premium": 1199,
    "Enterprise": 2999
}

contract_types = rng.choice(
    ["Monthly", "Quarterly", "Annual"],
    N_CUSTOMERS,
    p=[0.60, 0.25, 0.15]
)

discount_pct = rng.choice(
    [0, 5, 10, 15, 20],
    N_CUSTOMERS,
    p=[0.45, 0.20, 0.20, 0.10, 0.05]
)

subscriptions = pd.DataFrame({
    "subscription_id": make_ids("S", N_CUSTOMERS),
    "customer_id": customer_ids,
    "plan": plans,
    "contract_type": contract_types,
    "monthly_charges": [
        plan_prices[p] for p in plans
    ],
    "discount_pct": discount_pct,
    "payment_method": rng.choice(
        [
            "Credit Card",
            "Debit Card",
            "UPI",
            "Net Banking",
            "Auto Debit"
        ],
        N_CUSTOMERS,
        p=[0.25, 0.15, 0.35, 0.10, 0.15]
    ),
    "auto_renewal": rng.choice(
        [True, False],
        N_CUSTOMERS,
        p=[0.72, 0.28]
    ),
    "subscription_start_date": signup_dates
})


# ============================================================
# 3. CUSTOMER ACTIVITY
# ============================================================

print("[3/6] Generating customer activity...")

# ------------------------------------------------------------
# Latent engagement profile
#
# Beta distribution creates realistic variation between
# low and high engagement customers.
# ------------------------------------------------------------

base_engagement = (
    rng.beta(
        a=2.2,
        b=2.0,
        size=N_CUSTOMERS
    ) * 100
)

engagement_map = dict(
    zip(customer_ids, base_engagement)
)

customer_signup_map = dict(
    zip(customer_ids, signup_dates)
)

months = pd.date_range(
    START_DATE.to_period("M").start_time,
    END_DATE.to_period("M").start_time,
    freq="MS"
)

activity_records = []

for month in months:

    # Only customers who have already signed up
    eligible = [
        cid for cid in customer_ids
        if customer_signup_map[cid] <= (
            month + pd.offsets.MonthEnd(0)
        )
    ]

    if not eligible:
        continue

    eligible = np.array(eligible)

    # Activity probability based on engagement
    engagement_values = np.array([
        engagement_map[cid]
        for cid in eligible
    ])

    activity_probability = (
        0.35
        + 0.005 * engagement_values
    )

    active_mask = (
        rng.random(len(eligible))
        < np.clip(
            activity_probability,
            0.20,
            0.95
        )
    )

    active_customers = eligible[active_mask]

    if len(active_customers) == 0:
        continue

    month_df = pd.DataFrame({
        "customer_id": active_customers,
        "activity_date": month
    })

    engagement_values = np.array([
        engagement_map[cid]
        for cid in active_customers
    ])

    # --------------------------------------------------------
    # Behavioral metrics
    # --------------------------------------------------------

    login_lambda = np.clip(
        2 + engagement_values / 5,
        1,
        25
    )

    month_df["login_count"] = rng.poisson(
        login_lambda
    )

    month_df["session_count"] = (
        month_df["login_count"]
        + rng.poisson(
            2 + engagement_values / 20
        )
    )

    month_df["avg_session_minutes"] = np.clip(
        rng.normal(
            10 + engagement_values * 0.35,
            8,
            len(month_df)
        ),
        2,
        90
    ).round(2)

    month_df["features_used"] = np.clip(
        rng.poisson(
            1 + engagement_values / 15
        ),
        1,
        12
    )

    # Actual observed engagement
    month_df["engagement_score"] = np.clip(
        (
            month_df["login_count"] * 2
            + month_df["features_used"] * 3
            + month_df["avg_session_minutes"] * 0.8
        ),
        0,
        100
    ).round(2)

    activity_records.append(month_df)


activity = pd.concat(
    activity_records,
    ignore_index=True
)

activity.insert(
    0,
    "activity_id",
    make_ids(
        "A",
        len(activity),
        8
    )
)


# ============================================================
# 4. SUPPORT + TRANSACTIONS
# ============================================================

print("[4/6] Generating support and transactions...")

# Customer-level support tendency
support_tendency = rng.poisson(
    1.5,
    N_CUSTOMERS
)

support_map = dict(
    zip(customer_ids, support_tendency)
)

# ------------------------------------------------------------
# Support tickets
# ------------------------------------------------------------

ticket_count = int(N_CUSTOMERS * 1.8)

support_customer_ids = rng.choice(
    customer_ids,
    ticket_count
)

support = pd.DataFrame({
    "ticket_id": make_ids(
        "ST",
        ticket_count,
        8
    ),
    "customer_id": support_customer_ids,
    "ticket_date": pd.to_datetime(
        rng.integers(
            START_DATE.value // 10**9,
            END_DATE.value // 10**9,
            ticket_count
        ),
        unit="s"
    ),
    "issue_category": rng.choice(
        [
            "Technical",
            "Billing",
            "Account",
            "Performance",
            "Feature Request",
            "Other"
        ],
        ticket_count,
        p=[0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
    ),
    "priority": rng.choice(
        ["Low", "Medium", "High"],
        ticket_count,
        p=[0.50, 0.38, 0.12]
    ),
    "resolution_hours": np.clip(
        rng.gamma(
            shape=2.5,
            scale=5,
            size=ticket_count
        ),
        0.5,
        100
    ).round(2),
    "satisfaction_score": rng.choice(
        [1, 2, 3, 4, 5],
        ticket_count,
        p=[0.05, 0.10, 0.20, 0.35, 0.30]
    ),
    "resolved": rng.choice(
        [True, False],
        ticket_count,
        p=[0.92, 0.08]
    )
})


# ------------------------------------------------------------
# Transactions
# ------------------------------------------------------------

transaction_records = []

price_map = dict(
    zip(
        subscriptions["customer_id"],
        subscriptions["monthly_charges"]
    )
)

for month in months:

    eligible = [
        cid for cid in customer_ids
        if customer_signup_map[cid] <= (
            month + pd.offsets.MonthEnd(0)
        )
    ]

    eligible = np.array(eligible)

    if len(eligible) == 0:
        continue

    # Not every eligible customer pays successfully every month
    payment_mask = rng.random(
        len(eligible)
    ) < 0.88

    paying_customers = eligible[payment_mask]

    tx_df = pd.DataFrame({
        "customer_id": paying_customers
    })

    tx_df["transaction_date"] = (
        month
        + pd.to_timedelta(
            rng.integers(
                0,
                28,
                len(tx_df)
            ),
            unit="D"
        )
    )

    tx_df["transaction_type"] = rng.choice(
        ["Payment", "Refund"],
        len(tx_df),
        p=[0.96, 0.04]
    )

    tx_df["amount"] = (
        tx_df["customer_id"]
        .map(price_map)
        .astype(float)
    )

    # Revenue variation
    tx_df["amount"] *= rng.uniform(
        0.92,
        1.08,
        len(tx_df)
    )

    refund_mask = (
        tx_df["transaction_type"] == "Refund"
    )

    tx_df.loc[
        refund_mask,
        "amount"
    ] *= rng.uniform(
        0.10,
        0.50,
        refund_mask.sum()
    )

    tx_df["amount"] = tx_df["amount"].round(2)

    # Payment failures
    tx_df["payment_status"] = rng.choice(
        ["Success", "Failed"],
        len(tx_df),
        p=[0.93, 0.07]
    )

    transaction_records.append(tx_df)


transactions = pd.concat(
    transaction_records,
    ignore_index=True
)

transactions.insert(
    0,
    "transaction_id",
    make_ids(
        "T",
        len(transactions),
        9
    )
)


# ============================================================
# 5. CHURN
# ============================================================

print("[5/6] Generating behavior-based churn...")

activity_summary = (
    activity
    .groupby("customer_id")
    .agg(
        avg_engagement=(
            "engagement_score",
            "mean"
        ),
        avg_logins=(
            "login_count",
            "mean"
        ),
        avg_sessions=(
            "session_count",
            "mean"
        )
    )
    .reset_index()
)

payment_summary = (
    transactions
    .assign(
        failed=lambda x:
            (
                x["payment_status"]
                == "Failed"
            ).astype(int)
    )
    .groupby("customer_id")
    .agg(
        failed_payments=("failed", "sum")
    )
    .reset_index()
)

support_summary = (
    support
    .groupby("customer_id")
    .agg(
        support_tickets=(
            "ticket_id",
            "count"
        ),
        avg_satisfaction=(
            "satisfaction_score",
            "mean"
        )
    )
    .reset_index()
)

churn_base = (
    customers[
        [
            "customer_id",
            "signup_date"
        ]
    ]
    .merge(
        subscriptions[
            [
                "customer_id",
                "contract_type",
                "monthly_charges",
                "auto_renewal"
            ]
        ],
        on="customer_id"
    )
    .merge(
        activity_summary,
        on="customer_id",
        how="left"
    )
    .merge(
        payment_summary,
        on="customer_id",
        how="left"
    )
    .merge(
        support_summary,
        on="customer_id",
        how="left"
    )
)

churn_base = churn_base.fillna({
    "avg_engagement": 50,
    "avg_logins": 5,
    "avg_sessions": 6,
    "failed_payments": 0,
    "support_tickets": 0,
    "avg_satisfaction": 4
})


# ------------------------------------------------------------
# Tenure at analysis date
# ------------------------------------------------------------

analysis_date = END_DATE

churn_base["tenure_months"] = (
    (
        analysis_date
        - churn_base["signup_date"]
    ).dt.days / 30.44
)


# ------------------------------------------------------------
# Behavior-based risk score
# ------------------------------------------------------------

risk = np.full(
    len(churn_base),
    0.06
)

# Monthly contracts
risk += np.where(
    churn_base["contract_type"]
    == "Monthly",
    0.10,
    0
)

# Low engagement
risk += np.where(
    churn_base["avg_engagement"] < 30,
    0.18,
    0
)

risk += np.where(
    churn_base["avg_engagement"] < 50,
    0.08,
    0
)

# Payment failures
risk += np.minimum(
    churn_base["failed_payments"] * 0.025,
    0.15
)

# Support experience
risk += np.where(
    churn_base["avg_satisfaction"] < 3,
    0.12,
    0
)

risk += np.where(
    churn_base["support_tickets"] >= 6,
    0.07,
    0
)

# Early tenure
risk += np.where(
    churn_base["tenure_months"] <= 6,
    0.08,
    0
)

# No auto renewal
risk += np.where(
    churn_base["auto_renewal"] == False,
    0.05,
    0
)

# Small natural variation
risk += rng.normal(
    0,
    0.025,
    len(risk)
)

risk = np.clip(
    risk,
    0.01,
    0.75
)

churn_flag = rng.binomial(
    1,
    risk
)


# ------------------------------------------------------------
# Churn table
# ------------------------------------------------------------

churn = pd.DataFrame({
    "churn_id": make_ids(
        "CH",
        N_CUSTOMERS,
        7
    ),
    "customer_id": customer_ids,
    "churn_flag": churn_flag
})

churn_reasons = [
    "Price",
    "Poor Service",
    "Low Usage",
    "Technical Issues",
    "Competitor",
    "Payment Issues",
    "Missing Features",
    "Other"
]

churn["churn_reason"] = np.where(
    churn["churn_flag"] == 1,
    rng.choice(
        churn_reasons,
        N_CUSTOMERS
    ),
    None
)

churn["cancellation_channel"] = np.where(
    churn["churn_flag"] == 1,
    rng.choice(
        [
            "Website",
            "Mobile App",
            "Customer Support",
            "Email"
        ],
        N_CUSTOMERS
    ),
    None
)

# Churn dates
churn["churn_date"] = pd.NaT

churn_indices = np.where(
    churn_flag == 1
)[0]

for idx in churn_indices:

    signup = churn_base.loc[
        idx,
        "signup_date"
    ]

    max_days = max(
        30,
        (END_DATE - signup).days
    )

    if max_days >= 30:

        churn_date = (
            signup
            + pd.Timedelta(
                days=int(
                    rng.integers(
                        30,
                        max_days + 1
                    )
                )
            )
        )

        churn.loc[
            idx,
            "churn_date"
        ] = churn_date


# ============================================================
# 6. CONTROLLED DATA QUALITY ISSUES
# ============================================================

print("[6/6] Introducing controlled data-quality issues...")

# ------------------------------------------------------------
# Missing acquisition channels
# ------------------------------------------------------------

missing_idx = rng.choice(
    customers.index,
    500,
    replace=False
)

customers.loc[
    missing_idx,
    "acquisition_channel"
] = np.nan


# ------------------------------------------------------------
# Duplicate customer records
# ------------------------------------------------------------

duplicates = customers.sample(
    100,
    random_state=SEED
)

customers = pd.concat(
    [
        customers,
        duplicates
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Activity outliers
# ------------------------------------------------------------

outlier_idx = rng.choice(
    activity.index,
    150,
    replace=False
)

activity.loc[
    outlier_idx,
    "avg_session_minutes"
] *= 8


# ------------------------------------------------------------
# Missing support satisfaction
# ------------------------------------------------------------

support_missing_idx = rng.choice(
    support.index,
    200,
    replace=False
)

support.loc[
    support_missing_idx,
    "satisfaction_score"
] = np.nan


# ============================================================
# SAVE DATA
# ============================================================

print("\nSaving datasets...")

customers.to_csv(
    f"{OUTPUT_DIR}/customers.csv",
    index=False
)

subscriptions.to_csv(
    f"{OUTPUT_DIR}/subscriptions.csv",
    index=False
)

activity.to_csv(
    f"{OUTPUT_DIR}/customer_activity.csv",
    index=False
)

transactions.to_csv(
    f"{OUTPUT_DIR}/transactions.csv",
    index=False
)

support.to_csv(
    f"{OUTPUT_DIR}/support_tickets.csv",
    index=False
)

churn.to_csv(
    f"{OUTPUT_DIR}/churn.csv",
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATASET V2 GENERATED SUCCESSFULLY")
print("=" * 70)

print(
    f"Customers:       {len(customers):,}"
)

print(
    f"Subscriptions:   {len(subscriptions):,}"
)

print(
    f"Activity:        {len(activity):,}"
)

print(
    f"Transactions:    {len(transactions):,}"
)

print(
    f"Support:         {len(support):,}"
)

print(
    f"Churn records:   {len(churn):,}"
)

print(
    f"Churn rate:      "
    f"{churn['churn_flag'].mean() * 100:.2f}%"
)

print(
    f"Analysis date:   {END_DATE.date()}"
)

print("=" * 70)