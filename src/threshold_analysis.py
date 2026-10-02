# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# THRESHOLD ANALYSIS
# ============================================================

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
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
# 08. BASELINE PROBABILITY METRICS
# ============================================================

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

pr_auc = average_precision_score(
    y_test,
    probabilities
)

print("\nProbability-based Metrics")
print("-------------------------")
print(f"ROC-AUC : {roc_auc:.4f}")
print(f"PR-AUC  : {pr_auc:.4f}")


# ============================================================
# 09. THRESHOLD ANALYSIS
# ============================================================

thresholds = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70
]


results = []


for threshold in thresholds:

    predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1": f1
    })


threshold_results = pd.DataFrame(
    results
)


# ============================================================
# 10. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 65)
print("THRESHOLD ANALYSIS")
print("=" * 65)

print(
    threshold_results.round(4).to_string(
        index=False
    )
)


# ============================================================
# 11. BEST F1 THRESHOLD
# ============================================================

best_f1_row = threshold_results.loc[
    threshold_results["F1"].idxmax()
]

print("\n" + "=" * 65)
print("BEST F1 THRESHOLD")
print("=" * 65)

print(
    f"Threshold : "
    f"{best_f1_row['Threshold']:.2f}"
)

print(
    f"Precision : "
    f"{best_f1_row['Precision']:.4f}"
)

print(
    f"Recall    : "
    f"{best_f1_row['Recall']:.4f}"
)

print(
    f"F1 Score  : "
    f"{best_f1_row['F1']:.4f}"
)


# ============================================================
# 12. SAVE RESULTS
# ============================================================

output_path = "data/threshold_analysis.csv"

threshold_results.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved: {output_path}"
)


print("\n" + "=" * 65)
print("THRESHOLD ANALYSIS COMPLETED")
print("=" * 65)
