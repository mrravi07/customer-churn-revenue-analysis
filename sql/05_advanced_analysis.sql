-- ============================================================
-- CUSTOMER CHURN & REVENUE ANALYSIS
-- ADVANCED BUSINESS ANALYSIS
-- ============================================================


-- ============================================================
-- 01. CHURN REASON ANALYSIS
-- ============================================================

SELECT
    churn_reason,

    COUNT(*) AS churned_customers,

    ROUND(
        100.0 * COUNT(*)
        / NULLIF(
            (SELECT COUNT(*)
             FROM customer_360
             WHERE churn_flag = 1),
            0
        ),
        2
    ) AS churn_share_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS revenue_from_churned_customers,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_churned_customer_revenue

FROM customer_360

WHERE churn_flag = 1

GROUP BY churn_reason

ORDER BY churned_customers DESC;


-- ============================================================
-- 02. CANCELLATION CHANNEL ANALYSIS
-- ============================================================

SELECT
    cancellation_channel,

    COUNT(*) AS churned_customers,

    ROUND(
        100.0 * COUNT(*)
        / NULLIF(
            (SELECT COUNT(*)
             FROM customer_360
             WHERE churn_flag = 1),
            0
        ),
        2
    ) AS churn_share_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS revenue_from_churned_customers,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_churned_customer_revenue

FROM customer_360

WHERE churn_flag = 1

GROUP BY cancellation_channel

ORDER BY churned_customers DESC;




-- ============================================================
-- 03. REVENUE AT RISK FROM CHURNED CUSTOMERS
-- ============================================================

SELECT
    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    ROUND(
        (SUM(net_revenue) FILTER (
            WHERE churn_flag = 1
        ))::numeric,
        2
    ) AS churned_customer_revenue,

    ROUND(
        (SUM(net_revenue) FILTER (
            WHERE churn_flag = 0
        ))::numeric,
        2
    ) AS retained_customer_revenue,

    ROUND(
        (
            100.0 *
            SUM(net_revenue) FILTER (
                WHERE churn_flag = 1
            )
            / NULLIF(SUM(net_revenue), 0)
        )::numeric,
        2
    ) AS revenue_at_risk_pct,

    ROUND(
        (AVG(net_revenue) FILTER (
            WHERE churn_flag = 1
        ))::numeric,
        2
    ) AS avg_churned_customer_revenue

FROM customer_360;







-- ============================================================
-- 04. HIGH-VALUE CHURNED CUSTOMERS
-- ============================================================

SELECT
    customer_id,
    first_name,
    customer_segment,
    plan,
    contract_type,
    monthly_charges,
    tenure_months,
    avg_engagement_score,
    total_support_tickets,
    net_revenue,
    churn_reason,
    cancellation_channel,
    churn_date

FROM customer_360

WHERE churn_flag = 1

ORDER BY net_revenue DESC

LIMIT 20;





-- ============================================================
-- 05. FAILED PAYMENTS VS CHURN
-- ============================================================

SELECT
    CASE
        WHEN failed_payments = 0
            THEN '0 Failed Payments'

        WHEN failed_payments BETWEEN 1 AND 2
            THEN '1-2 Failed Payments'

        WHEN failed_payments BETWEEN 3 AND 5
            THEN '3-5 Failed Payments'

        ELSE '6+ Failed Payments'
    END AS failed_payment_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        (
            100.0 *
            COUNT(*) FILTER (
                WHERE churn_flag = 1
            )
            / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(monthly_charges)::numeric,
        2
    ) AS avg_monthly_charges

FROM customer_360

GROUP BY failed_payment_group

ORDER BY
    MIN(failed_payments);



-- ============================================================
-- 06. SUPPORT SATISFACTION VS CHURN
-- ============================================================

SELECT
    CASE
        WHEN avg_satisfaction_score = 0
            THEN 'No Support Rating'

        WHEN avg_satisfaction_score < 2
            THEN 'Very Low (1-2)'

        WHEN avg_satisfaction_score < 3
            THEN 'Low (2-3)'

        WHEN avg_satisfaction_score < 4
            THEN 'Moderate (3-4)'

        ELSE 'High (4-5)'
    END AS satisfaction_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        (
            100.0 *
            COUNT(*) FILTER (
                WHERE churn_flag = 1
            )
            / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(avg_satisfaction_score)::numeric,
        2
    ) AS avg_satisfaction_score,

    ROUND(
        AVG(avg_resolution_hours)::numeric,
        2
    ) AS avg_resolution_hours,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_360

GROUP BY satisfaction_group

ORDER BY
    MIN(avg_satisfaction_score);





-- ============================================================
-- 07. MONTHLY CHURN TREND
-- ============================================================

WITH monthly_customers AS (

    SELECT
        DATE_TRUNC('month', signup_date)::date AS month,

        COUNT(*) AS customers_started

    FROM customer_360

    GROUP BY 1
),

monthly_churn AS (

    SELECT
        DATE_TRUNC('month', churn_date)::date AS month,

        COUNT(*) AS churned_customers,

        ROUND(
            SUM(net_revenue)::numeric,
            2
        ) AS churned_revenue

    FROM customer_360

    WHERE churn_flag = 1
      AND churn_date IS NOT NULL

    GROUP BY 1
)

SELECT
    mc.month,

    mc.customers_started,

    COALESCE(
        mch.churned_customers,
        0
    ) AS churned_customers,

    COALESCE(
        mch.churned_revenue,
        0
    ) AS churned_revenue

FROM monthly_customers mc

LEFT JOIN monthly_churn mch
    ON mc.month = mch.month

ORDER BY mc.month;




-- ============================================================
-- 08. CUSTOMER RISK SEGMENTATION
-- ============================================================

WITH risk_scoring AS (

    SELECT
        customer_id,
        first_name,
        customer_segment,
        plan,
        contract_type,
        monthly_charges,
        tenure_months,
        avg_engagement_score,
        failed_payments,
        avg_satisfaction_score,
        total_support_tickets,
        net_revenue,
        churn_flag,

        (
            CASE
                WHEN avg_engagement_score < 40
                    THEN 2
                WHEN avg_engagement_score < 60
                    THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN failed_payments >= 3
                    THEN 2
                WHEN failed_payments >= 1
                    THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN avg_satisfaction_score > 0
                     AND avg_satisfaction_score < 3
                    THEN 2
                WHEN avg_satisfaction_score > 0
                     AND avg_satisfaction_score < 4
                    THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN contract_type = 'Monthly'
                    THEN 1
                ELSE 0
            END

        ) AS risk_score

    FROM customer_360
)

SELECT
    CASE
        WHEN risk_score >= 5
            THEN 'High Risk'

        WHEN risk_score >= 3
            THEN 'Medium Risk'

        ELSE 'Low Risk'
    END AS risk_segment,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        (
            100.0 *
            COUNT(*) FILTER (
                WHERE churn_flag = 1
            )
            / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(risk_score)::numeric,
        2
    ) AS avg_risk_score

FROM risk_scoring

GROUP BY
    CASE
        WHEN risk_score >= 5
            THEN 'High Risk'
        WHEN risk_score >= 3
            THEN 'Medium Risk'
        ELSE 'Low Risk'
    END

ORDER BY avg_risk_score DESC;



-- ============================================================
-- 09. CUSTOMER COHORT ANALYSIS
-- ============================================================

WITH cohort_data AS (

    SELECT
        customer_id,

        DATE_TRUNC(
            'quarter',
            signup_date
        )::date AS signup_cohort,

        churn_flag,

        net_revenue

    FROM customer_360
)

SELECT
    signup_cohort,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        (
            100.0 *
            COUNT(*) FILTER (
                WHERE churn_flag = 1
            )
            / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_cohort_revenue

FROM cohort_data

GROUP BY signup_cohort

ORDER BY signup_cohort;





-- ============================================================
-- 10. TOP REVENUE CUSTOMERS
-- ============================================================

SELECT
    customer_id,
    first_name,
    customer_segment,
    plan,
    contract_type,
    monthly_charges,
    tenure_months,
    avg_engagement_score,
    total_support_tickets,
    failed_payments,
    net_revenue,
    churn_flag,
    churn_reason

FROM customer_360

ORDER BY net_revenue DESC

LIMIT 20;





WITH customer_risk AS (

    SELECT
        customer_id,
        customer_segment,
        plan,
        contract_type,
        monthly_charges,
        tenure_months,
        avg_engagement_score,
        failed_payments,
        avg_satisfaction_score,
        net_revenue,
        churn_flag,

        (
            CASE
                WHEN avg_engagement_score < 40 THEN 2
                WHEN avg_engagement_score < 60 THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN failed_payments >= 3 THEN 2
                WHEN failed_payments >= 1 THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN avg_satisfaction_score > 0
                     AND avg_satisfaction_score < 3 THEN 2
                WHEN avg_satisfaction_score > 0
                     AND avg_satisfaction_score < 4 THEN 1
                ELSE 0
            END

            +

            CASE
                WHEN contract_type = 'Monthly' THEN 1
                ELSE 0
            END
        ) AS risk_score

    FROM customer_360
)

SELECT
    CASE
        WHEN risk_score >= 5 THEN 'High Risk'
        WHEN risk_score >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_segment,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    ROUND(
        (
            100.0 *
            COUNT(*) FILTER (WHERE churn_flag = 1)
            / NULLIF(COUNT(*), 0)
        )::numeric,
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_revenue,

    ROUND(
        (
            SUM(net_revenue) FILTER (
                WHERE churn_flag = 1
            )
        )::numeric,
        2
    ) AS churned_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_risk

GROUP BY
    CASE
        WHEN risk_score >= 5 THEN 'High Risk'
        WHEN risk_score >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END

ORDER BY
    MIN(risk_score) DESC;