<div align="center">

# Customer Churn & Revenue Analysis

### Customer Analytics | Churn Analysis | Revenue Intelligence

<p>
An end-to-end data analytics project focused on understanding customer churn,
revenue performance, customer behavior, and business KPIs through Python,
SQL, PostgreSQL, and Power BI.
</p>

<p>
<a href="https://github.com/mrravi07/customer-churn-revenue-analysis">
<img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>
</p>

</div>

---

## Overview

**Customer Churn & Revenue Analysis** is an end-to-end analytics project designed to transform raw customer and transaction data into a structured **Customer 360 analytical layer** and actionable business insights.

The project covers the complete analytics workflow — from **data profiling and cleaning to PostgreSQL integration, analytical SQL, business KPI development, customer segmentation, churn analysis, revenue analysis, and Power BI visualization**.

The objective is to help businesses understand:

- Which customers are at risk of churn
- How churn impacts revenue
- Which customer segments generate the most value
- Customer purchasing and engagement behavior
- Revenue contribution across different segments
- Key business KPIs and performance trends

---

## Project Architecture

```text
                    RAW CUSTOMER DATA
                           │
                           ▼
                  ┌─────────────────┐
                  │ DATA PROFILING  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ DATA CLEANING   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ DATA VALIDATION │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   POSTGRESQL    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ CUSTOMER 360    │
                  │     VIEW        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ ANALYTICAL SQL  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     POWER BI    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ BUSINESS        │
                  │ INSIGHTS        │
                  └─────────────────┘
