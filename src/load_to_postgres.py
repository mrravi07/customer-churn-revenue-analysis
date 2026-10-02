import os
import pandas as pd
from sqlalchemy import create_engine, text


# ============================================================
# DATABASE CONFIGURATION
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

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# DATA CONFIGURATION
# ============================================================

DATA_DIR = "data/cleaned"

TABLES = {
    "customers_cleaned.csv": "dim_customer",
    "subscriptions_cleaned.csv": "dim_subscription",
    "customer_activity_cleaned.csv": "fact_customer_activity",
    "transactions_cleaned.csv": "fact_transactions",
    "support_tickets_cleaned.csv": "fact_support",
    "churn_cleaned.csv": "fact_churn"
}


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

print("=" * 70)
print("POSTGRESQL CONNECTION TEST")
print("=" * 70)

try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.fetchone()[0]

        print("✅ PostgreSQL connection successful")
        print(version)

except Exception as e:

    print("❌ Database connection failed")
    print(e)

    raise SystemExit


# ============================================================
# LOAD TABLES
# ============================================================

print("\n" + "=" * 70)
print("LOADING DATA INTO POSTGRESQL")
print("=" * 70)

for filename, table_name in TABLES.items():

    path = os.path.join(
        DATA_DIR,
        filename
    )

    print(f"\nLoading: {filename}")

    df = pd.read_csv(path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
        chunksize=10_000,
        method="multi"
    )

    print(
        f"✅ Loaded into table: {table_name}"
    )


# ============================================================
# VERIFY TABLES
# ============================================================

print("\n" + "=" * 70)
print("TABLE VERIFICATION")
print("=" * 70)

with engine.connect() as connection:

    for table_name in TABLES.values():

        result = connection.execute(
            text(
                f"SELECT COUNT(*) "
                f"FROM {table_name}"
            )
        )

        count = result.scalar()

        print(
            f"{table_name:30} → "
            f"{count:,} rows"
        )


print("\n" + "=" * 70)
print("DATABASE LOADING COMPLETED")
print("=" * 70)

print("✅ All cleaned datasets are now in PostgreSQL.")