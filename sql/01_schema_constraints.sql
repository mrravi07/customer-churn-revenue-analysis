-- ============================================================
-- CUSTOMER CHURN & REVENUE ANALYSIS
-- DATABASE CONSTRAINTS
-- ============================================================

ALTER TABLE dim_customer
ADD CONSTRAINT pk_dim_customer
PRIMARY KEY (customer_id);

ALTER TABLE dim_subscription
ADD CONSTRAINT pk_dim_subscription
PRIMARY KEY (subscription_id);

ALTER TABLE fact_customer_activity
ADD CONSTRAINT pk_fact_customer_activity
PRIMARY KEY (activity_id);

ALTER TABLE fact_transactions
ADD CONSTRAINT pk_fact_transactions
PRIMARY KEY (transaction_id);

ALTER TABLE fact_support
ADD CONSTRAINT pk_fact_support
PRIMARY KEY (ticket_id);

ALTER TABLE fact_churn
ADD CONSTRAINT pk_fact_churn
PRIMARY KEY (churn_id);


-- FOREIGN KEYS

ALTER TABLE dim_subscription
ADD CONSTRAINT fk_subscription_customer
FOREIGN KEY (customer_id)
REFERENCES dim_customer(customer_id);

ALTER TABLE fact_customer_activity
ADD CONSTRAINT fk_activity_customer
FOREIGN KEY (customer_id)
REFERENCES dim_customer(customer_id);

ALTER TABLE fact_transactions
ADD CONSTRAINT fk_transactions_customer
FOREIGN KEY (customer_id)
REFERENCES dim_customer(customer_id);

ALTER TABLE fact_support
ADD CONSTRAINT fk_support_customer
FOREIGN KEY (customer_id)
REFERENCES dim_customer(customer_id);

ALTER TABLE fact_churn
ADD CONSTRAINT fk_churn_customer
FOREIGN KEY (customer_id)
REFERENCES dim_customer(customer_id);


-- CHECK CONSTRAINTS

ALTER TABLE dim_customer
ADD CONSTRAINT chk_customer_age
CHECK (age >= 18 AND age <= 100);

ALTER TABLE dim_subscription
ADD CONSTRAINT chk_monthly_charges
CHECK (monthly_charges > 0);

ALTER TABLE dim_subscription
ADD CONSTRAINT chk_discount
CHECK (discount_pct >= 0 AND discount_pct <= 100);

ALTER TABLE fact_customer_activity
ADD CONSTRAINT chk_login_count
CHECK (login_count >= 0);

ALTER TABLE fact_customer_activity
ADD CONSTRAINT chk_session_count
CHECK (session_count >= 0);

ALTER TABLE fact_customer_activity
ADD CONSTRAINT chk_engagement_score
CHECK (
    engagement_score >= 0
    AND engagement_score <= 100
);

ALTER TABLE fact_transactions
ADD CONSTRAINT chk_transaction_amount
CHECK (amount > 0);

ALTER TABLE fact_support
ADD CONSTRAINT chk_satisfaction_score
CHECK (
    satisfaction_score >= 1
    AND satisfaction_score <= 5
);

ALTER TABLE fact_support
ADD CONSTRAINT chk_resolution_hours
CHECK (resolution_hours >= 0);

ALTER TABLE fact_churn
ADD CONSTRAINT chk_churn_flag
CHECK (churn_flag IN (0, 1));