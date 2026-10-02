# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# CHURN PREDICTION MODEL
# ============================================================

import os
import pandas as pd
import numpy as np

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 01. DATABASE CONNECTION
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

engine = create_engine(DATABASE_URL)


# ============================================================
# 02. LOAD CUSTOMER 360 DATA
# ============================================================

print("\nLoading customer_360 data...")

query = """
SELECT *
FROM customer_360;
"""

df = pd.read_sql(query, engine)

print(f"Rows loaded    : {len(df):,}")
print(f"Columns loaded : {len(df.columns)}")


# ============================================================
# 03. BASIC DATA CHECK
# ============================================================

print("\nTarget Distribution:")
print(df["churn_flag"].value_counts())

print("\nTarget Percentage:")
print(
    df["churn_flag"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# 04. REMOVE TARGET LEAKAGE
# ============================================================

leakage_columns = [
    "customer_id",
    "first_name",
    "churn_flag",
    "churn_date",
    "churn_reason",
    "cancellation_channel"
]

X = df.drop(
    columns=leakage_columns,
    errors="ignore"
)

y = df["churn_flag"]


# ============================================================
# 05. IDENTIFY FEATURE TYPES
# ============================================================

categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=["int64", "float64", "int32", "float32"]
).columns.tolist()

print("\nCategorical Features:")
print(categorical_features)

print("\nNumeric Features:")
print(numeric_features)


# ============================================================
# 06. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=2026,
    stratify=y
)

print("\nTrain/Test Split")
print("----------------")
print(f"Training rows : {len(X_train):,}")
print(f"Testing rows  : {len(X_test):,}")


# ============================================================
# 07. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
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
# 08. LOGISTIC REGRESSION
# ============================================================

logistic_model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=2026
            )
        )
    ]
)


print("\nTraining Logistic Regression...")

logistic_model.fit(
    X_train,
    y_train
)

logistic_probability = logistic_model.predict_proba(
    X_test
)[:, 1]

logistic_prediction = (
    logistic_probability >= 0.50
).astype(int)


# ============================================================
# 09. RANDOM FOREST
# ============================================================

random_forest_model = Pipeline(
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

random_forest_model.fit(
    X_train,
    y_train
)

rf_probability = random_forest_model.predict_proba(
    X_test
)[:, 1]

rf_prediction = (
    rf_probability >= 0.50
).astype(int)


# ============================================================
# 10. MODEL EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    model_name,
    y_true,
    y_prediction,
    y_probability
):

    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    accuracy = accuracy_score(
        y_true,
        y_prediction
    )

    precision = precision_score(
        y_true,
        y_prediction,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_prediction,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_prediction,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_true,
        y_probability
    )

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_true,
            y_prediction
        )
    )

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_prediction,
            zero_division=0
        )
    )

    return {
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC_AUC": roc_auc
    }


# ============================================================
# 11. EVALUATE MODELS
# ============================================================

logistic_results = evaluate_model(
    "Logistic Regression",
    y_test,
    logistic_prediction,
    logistic_probability
)


rf_results = evaluate_model(
    "Random Forest",
    y_test,
    rf_prediction,
    rf_probability
)


# ============================================================
# 12. MODEL COMPARISON
# ============================================================

results = pd.DataFrame([
    logistic_results,
    rf_results
])

results = results.round(4)

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(results.to_string(index=False))


# ============================================================
# 13. SAVE MODEL RESULTS
# ============================================================

output_path = "data/model_results.csv"

results.to_csv(
    output_path,
    index=False
)

print(
    f"\nModel comparison saved to: {output_path}"
)


# ============================================================
# 14. RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

rf_preprocessor = (
    random_forest_model
    .named_steps["preprocessor"]
)

rf_classifier = (
    random_forest_model
    .named_steps["model"]
)

feature_names = (
    rf_preprocessor
    .get_feature_names_out()
)

importance = (
    rf_classifier
    .feature_importances_
)

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
})

feature_importance = (
    feature_importance
    .sort_values(
        "importance",
        ascending=False
    )
    .head(20)
)

feature_importance = (
    feature_importance
    .round({"importance": 6})
)

print("\n" + "=" * 60)
print("TOP 20 RANDOM FOREST FEATURES")
print("=" * 60)

print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# 15. SAVE FEATURE IMPORTANCE
# ============================================================

feature_importance.to_csv(
    "data/feature_importance.csv",
    index=False
)

print(
    "\nFeature importance saved to: "
    "data/feature_importance.csv"
)


print("\n" + "=" * 60)
print("CHURN MODELING COMPLETED")
print("=" * 60)