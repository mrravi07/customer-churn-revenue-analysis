-- ============================================================
-- CUSTOMER CHURN & REVENUE ANALYSIS
-- ANALYTICAL SQL QUERIES
-- ============================================================

-- ============================================================
-- 01. EXECUTIVE KPI
-- ============================================================

SELECT
    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(monthly_charges)::numeric,
        2
    ) AS avg_monthly_charges,

    ROUND(
        AVG(avg_engagement_score)::numeric,
        2
    ) AS avg_engagement_score,

    ROUND(
        AVG(total_support_tickets)::numeric,
        2
    ) AS avg_support_tickets

FROM customer_360;


-- ============================================================
-- 02. CUSTOMER SEGMENT ANALYSIS
-- ============================================================

SELECT
    customer_segment,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_360

GROUP BY customer_segment

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 03. PLAN-WISE CHURN & REVENUE
-- ============================================================

SELECT
    plan,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(monthly_charges)::numeric,
        2
    ) AS avg_monthly_charges

FROM customer_360

GROUP BY plan

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 04. CONTRACT TYPE ANALYSIS
-- ============================================================

SELECT
    contract_type,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue,

    ROUND(
        AVG(monthly_charges)::numeric,
        2
    ) AS avg_monthly_charges

FROM customer_360

GROUP BY contract_type

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 05. ACQUISITION CHANNEL ANALYSIS
-- ============================================================

SELECT
    acquisition_channel,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_360

GROUP BY acquisition_channel

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 06. PAYMENT METHOD & FAILED PAYMENTS
-- ============================================================

SELECT
    payment_method,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    SUM(failed_payments) AS total_failed_payments,

    ROUND(
        AVG(failed_payments)::numeric,
        2
    ) AS avg_failed_payments,

    ROUND(
        SUM(net_revenue)::numeric,
        2
    ) AS total_net_revenue

FROM customer_360

GROUP BY payment_method

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 07. TENURE ANALYSIS
-- ============================================================

SELECT
    CASE
        WHEN tenure_months <= 3
            THEN '0-3 Months'

        WHEN tenure_months <= 6
            THEN '4-6 Months'

        WHEN tenure_months <= 12
            THEN '7-12 Months'

        WHEN tenure_months <= 24
            THEN '13-24 Months'

        ELSE '25+ Months'
    END AS tenure_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(avg_engagement_score)::numeric,
        2
    ) AS avg_engagement_score,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_360

GROUP BY tenure_group

ORDER BY
    MIN(tenure_months);


-- ============================================================
-- 08. ENGAGEMENT VS CHURN
-- ============================================================

SELECT
    CASE
        WHEN avg_engagement_score <= 20
            THEN 'Very Low'

        WHEN avg_engagement_score <= 40
            THEN 'Low'

        WHEN avg_engagement_score <= 60
            THEN 'Moderate'

        WHEN avg_engagement_score <= 80
            THEN 'High'

        ELSE 'Very High'
    END AS engagement_group,

    COUNT(*) AS total_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 1
    ) AS churned_customers,

    COUNT(*) FILTER (
        WHERE churn_flag = 0
    ) AS retained_customers,

    ROUND(
        100.0 *
        COUNT(*) FILTER (WHERE churn_flag = 1)
        / NULLIF(COUNT(*), 0),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(avg_monthly_logins)::numeric,
        2
    ) AS avg_monthly_logins,

    ROUND(
        AVG(total_support_tickets)::numeric,
        2
    ) AS avg_support_tickets,

    ROUND(
        AVG(net_revenue)::numeric,
        2
    ) AS avg_customer_revenue

FROM customer_360

GROUP BY engagement_group

ORDER BY
    MIN(avg_engagement_score);