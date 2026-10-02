-- ============================================================
-- CUSTOMER 360 ANALYTICAL VIEW
-- ============================================================

DROP VIEW IF EXISTS customer_360;


CREATE VIEW customer_360 AS

WITH activity_metrics AS (

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

        MAX(activity_date) AS last_activity_date

    FROM fact_customer_activity

    GROUP BY customer_id
),


revenue_metrics AS (

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

        COUNT(
            CASE
                WHEN transaction_type = 'Payment'
                 AND payment_status = 'Success'
                THEN 1
            END
        ) AS successful_payments,

        COUNT(
            CASE
                WHEN payment_status = 'Failed'
                THEN 1
            END
        ) AS failed_payments

    FROM fact_transactions

    GROUP BY customer_id
),


support_metrics AS (

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

    GROUP BY customer_id
)


SELECT

    c.customer_id,

    c.first_name,

    c.age,

    c.gender,

    c.city,

    c.state,

    c.signup_date::date AS signup_date,

    c.acquisition_channel,

    c.customer_segment,

    s.plan,

    s.contract_type,

    s.monthly_charges,

    s.discount_pct,

    s.payment_method,

    s.auto_renewal,

    -- --------------------------------------------------------
    -- TENURE
    -- --------------------------------------------------------

    ROUND(
    	(
        	DATE '2026-06-30' - c.signup_date::date
   		) / 30.44,
    	1
	) AS tenure_months,
    -- --------------------------------------------------------
    -- ACTIVITY
    -- --------------------------------------------------------

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

    a.last_activity_date::date AS last_activity_date,

    -- --------------------------------------------------------
    -- REVENUE
    -- --------------------------------------------------------

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

    -- --------------------------------------------------------
    -- SUPPORT
    -- --------------------------------------------------------

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

    -- --------------------------------------------------------
    -- CHURN
    -- --------------------------------------------------------

    ch.churn_flag,

    ch.churn_date::date AS churn_date,

    ch.churn_reason,

    ch.cancellation_channel

	
FROM dim_customer c

LEFT JOIN dim_subscription s
    ON c.customer_id = s.customer_id

LEFT JOIN activity_metrics a
    ON c.customer_id = a.customer_id

LEFT JOIN revenue_metrics r
    ON c.customer_id = r.customer_id

LEFT JOIN support_metrics sm
    ON c.customer_id = sm.customer_id

LEFT JOIN fact_churn ch
    ON c.customer_id = ch.customer_id;
    