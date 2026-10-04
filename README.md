# Customer Churn & Revenue Analysis

An end-to-end **Customer Churn & Revenue Analytics** project built to analyze customer behavior, identify churn drivers, quantify revenue at risk, and develop a leakage-free machine learning model for churn prediction.

The project integrates **Python, Pandas, PostgreSQL, Advanced SQL, Statistical Analysis, Machine Learning, SHAP Explainability, and Power BI** into a complete analytics workflow.

---

## 📌 Project Overview

Customer churn is one of the most important business problems for subscription-based businesses.

This project analyzes a customer base of **50,000 customers** to answer key business questions:

- What percentage of customers are churning?
- Which customer segments have the highest churn?
- Does contract type influence churn?
- How does customer engagement relate to churn?
- Do failed payments indicate higher churn risk?
- Does customer support satisfaction relate to churn?
- How much revenue is associated with churned customers?
- Which customer characteristics are most important for churn prediction?
- Can machine learning identify customers with higher churn probability?
- How can churn insights be converted into actionable business recommendations?

The project follows a complete analytics lifecycle from **raw data generation and quality validation to PostgreSQL analytics, machine learning, explainability, and Power BI visualization**.

---

# 🎯 Business Objectives

### Customer Analytics
- Analyze customer demographics and subscription behavior.
- Understand customer engagement patterns.
- Segment customers based on churn behavior.

### Churn Analysis
- Calculate overall churn rate.
- Identify high-churn customer groups.
- Analyze churn by:
  - Contract Type
  - Customer Segment
  - Subscription Plan
  - Engagement Level
  - Payment Method
  - Acquisition Channel
  - Tenure
  - Support Satisfaction
  - Failed Payments

### Revenue Analytics
- Calculate total net revenue.
- Measure revenue associated with churned customers.
- Identify high-value churned customers.
- Quantify revenue exposure associated with customer churn.

### Predictive Analytics
- Build a leakage-free churn prediction dataset.
- Compare Logistic Regression and Random Forest.
- Evaluate ROC-AUC and PR-AUC.
- Optimize the classification threshold.
- Analyze feature importance.
- Explain model behavior using SHAP.

---

# 🏗️ End-to-End Architecture

```text
                    RAW CUSTOMER DATA
                           │
                           ▼
                  DATA PROFILING
                           │
                           ▼
                    DATA CLEANING
                           │
                           ▼
               AUTOMATED DATA VALIDATION
                           │
                           ▼
                      POSTGRESQL
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        SQL ANALYSIS   CUSTOMER 360   INDEXING
              │            │
              └────────────┼────────────┘
                           ▼
                  ADVANCED ANALYTICS
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        STATISTICAL ANALYSIS       ML DATASET
                                        │
                                        ▼
                              LEAKAGE-FREE ML
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                LOGISTIC REGRESSION              RANDOM FOREST
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                              MODEL EVALUATION
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                    ROC / PR       Threshold       Feature
                     Curves         Analysis       Importance
                                        │
                                        ▼
                                SHAP EXPLAINABILITY
                                        │
                                        ▼
                               BUSINESS INSIGHTS
                                        │
                                        ▼
                                  POWER BI
                                   DASHBOARD
