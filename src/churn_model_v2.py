# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# LEAKAGE-FREE CHURN MODEL V2
# ============================================================

import pandas as pd

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
    average_precision_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# 01. LOAD DATASET
# ============================================================

DATA_PATH = "data/ml_dataset.csv"

print("\nLoading leakage-free ML dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Rows loaded    : {len(df):,}")
print(f"Columns loaded : {len(df.columns)}")


# ============================================================
# 02. REMOVE NON-PREDICTIVE / DATE COLUMNS
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

print("\nCategorical Features:")
print(categorical_features)

print("\nNumeric Features:")
print(numeric_features)


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

print("\nTrain/Test Split")
print("----------------")
print(f"Training rows : {len(X_train):,}")
print(f"Testing rows  : {len(X_test):,}")


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
# 06. LOGISTIC REGRESSION
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
                max_iter=2000,
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

logistic_probability = (
    logistic_model
    .predict_proba(X_test)[:, 1]
)

logistic_prediction = (
    logistic_probability >= 0.50
).astype(int)


# ============================================================
# 07. RANDOM FOREST
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

rf_probability = (
    random_forest_model
    .predict_proba(X_test)[:, 1]
)

rf_prediction = (
    rf_probability >= 0.50
).astype(int)


# ============================================================
# 08. MODEL EVALUATION
# ============================================================

def evaluate_model(
    model_name,
    y_true,
    y_prediction,
    y_probability
):

    print("\n" + "=" * 65)
    print(model_name)
    print("=" * 65)

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

    pr_auc = average_precision_score(
        y_true,
        y_probability
    )

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")
    print(f"PR-AUC    : {pr_auc:.4f}")

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
        "ROC_AUC": roc_auc,
        "PR_AUC": pr_auc
    }


# ============================================================
# 09. EVALUATE BOTH MODELS
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
# 10. MODEL COMPARISON
# ============================================================

results = pd.DataFrame([
    logistic_results,
    rf_results
])

results = results.round(4)

print("\n" + "=" * 65)
print("MODEL COMPARISON")
print("=" * 65)

print(
    results.to_string(index=False)
)


# ============================================================
# 11. SAVE MODEL RESULTS
# ============================================================

results.to_csv(
    "data/model_results_v2.csv",
    index=False
)

print(
    "\nSaved: data/model_results_v2.csv"
)


# ============================================================
# 12. RANDOM FOREST FEATURE IMPORTANCE
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


print("\n" + "=" * 65)
print("TOP 20 RANDOM FOREST FEATURES")
print("=" * 65)

print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# 13. SAVE FEATURE IMPORTANCE
# ============================================================

feature_importance.to_csv(
    "data/feature_importance_v2.csv",
    index=False
)

print(
    "\nSaved: data/feature_importance_v2.csv"
)


# ============================================================
# 14. COMPLETION
# ============================================================

print("\n" + "=" * 65)
print("LEAKAGE-FREE CHURN MODELING COMPLETED")
print("=" * 65)