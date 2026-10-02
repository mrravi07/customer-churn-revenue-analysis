-- ============================================================
-- PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_customer_state
ON dim_customer(state);

CREATE INDEX idx_customer_segment
ON dim_customer(customer_segment);

CREATE INDEX idx_customer_acquisition
ON dim_customer(acquisition_channel);

CREATE INDEX idx_customer_signup_date
ON dim_customer(signup_date);

CREATE INDEX idx_subscription_customer
ON dim_subscription(customer_id);

CREATE INDEX idx_subscription_plan
ON dim_subscription(plan);

CREATE INDEX idx_subscription_contract
ON dim_subscription(contract_type);

CREATE INDEX idx_subscription_payment
ON dim_subscription(payment_method);

CREATE INDEX idx_activity_customer
ON fact_customer_activity(customer_id);

CREATE INDEX idx_activity_date
ON fact_customer_activity(activity_date);

CREATE INDEX idx_activity_customer_date
ON fact_customer_activity(customer_id, activity_date);

CREATE INDEX idx_transactions_customer
ON fact_transactions(customer_id);

CREATE INDEX idx_transactions_date
ON fact_transactions(transaction_date);

CREATE INDEX idx_transactions_customer_date
ON fact_transactions(customer_id, transaction_date);

CREATE INDEX idx_transactions_status
ON fact_transactions(payment_status);

CREATE INDEX idx_support_customer
ON fact_support(customer_id);

CREATE INDEX idx_support_date
ON fact_support(ticket_date);

CREATE INDEX idx_support_category
ON fact_support(issue_category);

CREATE INDEX idx_churn_customer
ON fact_churn(customer_id);

CREATE INDEX idx_churn_date
ON fact_churn(churn_date);

CREATE INDEX idx_churn_flag
ON fact_churn(churn_flag);

