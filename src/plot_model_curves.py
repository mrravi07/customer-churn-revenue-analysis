# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# MODEL EVALUATION CURVES
# ============================================================

import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)


# ============================================================
# 01. LOAD DATA
# ============================================================

DATA_PATH = "data/ml_dataset.csv"

print("\nLoading ML dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Rows loaded: {len(df):,}")


# ============================================================
# 02. FEATURES / TARGET
# ============================================================

drop_columns = [
    "customer_id",
    "first_name",
    "signup_date",
    "last_activity_date",
    "churn_flag"
]

X = df.drop(
    columns=drop_columns,
    errors="ignore"
)

y = df["churn_flag"]


# ============================================================
# 03. FEATURE TYPES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=["int64", "float64", "int32", "float32"]
).columns.tolist()


# ============================================================
# 04. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=2026,
    stratify=y
)


# ============================================================
# 05. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ============================================================
# 06. RANDOM FOREST
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_split=10,
                min_samples_leaf=4,
                class_weight="balanced",
                random_state=2026,
                n_jobs=-1
            )
        )
    ]
)


print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# 07. PREDICT PROBABILITIES
# ============================================================

probabilities = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 08. ROC CURVE
# ============================================================

fpr, tpr, _ = roc_curve(
    y_test,
    probabilities
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)


plt.figure(figsize=(8, 6))

plt.plot(
    fpr,
    tpr,
    linewidth=2,
    label=f"Random Forest (ROC-AUC = {roc_auc:.4f})"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    linewidth=1
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title(
    "ROC Curve - Customer Churn Prediction"
)

plt.legend(
    loc="lower right"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

os.makedirs(
    "data/model_plots",
    exist_ok=True
)

roc_path = (
    "data/model_plots/"
    "random_forest_roc_curve.png"
)

plt.savefig(
    roc_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"\nROC Curve saved to: {roc_path}"
)


# ============================================================
# 09. PRECISION-RECALL CURVE
# ============================================================

precision, recall, _ = precision_recall_curve(
    y_test,
    probabilities
)

pr_auc = average_precision_score(
    y_test,
    probabilities
)


plt.figure(figsize=(8, 6))

plt.plot(
    recall,
    precision,
    linewidth=2,
    label=f"Random Forest (PR-AUC = {pr_auc:.4f})"
)

plt.xlabel("Recall")
plt.ylabel("Precision")

plt.title(
    "Precision-Recall Curve - Customer Churn Prediction"
)

plt.legend(
    loc="upper right"
)

plt.grid(
    alpha=0.3
)

plt.tight_layout()

pr_path = (
    "data/model_plots/"
    "random_forest_precision_recall_curve.png"
)

plt.savefig(
    pr_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"Precision-Recall Curve saved to: {pr_path}"
)


# ============================================================
# 10. FINAL METRICS
# ============================================================

print("\n" + "=" * 65)
print("MODEL CURVE SUMMARY")
print("=" * 65)

print(
    f"ROC-AUC : {roc_auc:.4f}"
)

print(
    f"PR-AUC  : {pr_auc:.4f}"
)

print("=" * 65)
