# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# SHAP MODEL EXPLAINABILITY
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import shap

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier


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
# 07. TRANSFORM TEST DATA
# ============================================================

print("\nTransforming test data...")

X_test_transformed = (
    model
    .named_steps["preprocessor"]
    .transform(X_test)
)

feature_names = (
    model
    .named_steps["preprocessor"]
    .get_feature_names_out()
)

print(
    f"Transformed features: {len(feature_names):,}"
)


# ============================================================
# 08. SAMPLE FOR SHAP
# ============================================================

SAMPLE_SIZE = min(
    2000,
    X_test_transformed.shape[0]
)

X_sample = X_test_transformed[
    :SAMPLE_SIZE
]

print(
    f"SHAP sample size: {SAMPLE_SIZE:,}"
)


# ============================================================
# 09. CONVERT TO DENSE MATRIX
# ============================================================

if hasattr(X_sample, "toarray"):
    X_sample = X_sample.toarray()


# ============================================================
# 10. SHAP EXPLAINER
# ============================================================

print("\nCalculating SHAP values...")

rf_model = (
    model
    .named_steps["model"]
)

explainer = shap.TreeExplainer(
    rf_model
)

shap_values = explainer.shap_values(
    X_sample
)


# ============================================================
# 11. HANDLE SHAP OUTPUT
# ============================================================

if isinstance(shap_values, list):

    # Older SHAP versions
    # Binary classification:
    # class 1 = churn

    shap_churn = shap_values[1]

else:

    # Newer SHAP versions may return:
    # (samples, features, classes)

    if len(shap_values.shape) == 3:

        # Class 1 = churn
        shap_churn = shap_values[:, :, 1]

    else:

        shap_churn = shap_values


print(
    f"SHAP values shape: {shap_churn.shape}"
)


# ============================================================
# 12. GLOBAL SHAP IMPORTANCE
# ============================================================

mean_abs_shap = (
    abs(shap_churn)
    .mean(axis=0)
)

shap_importance = pd.DataFrame({
    "feature": feature_names,
    "mean_abs_shap": mean_abs_shap
})

shap_importance = (
    shap_importance
    .sort_values(
        "mean_abs_shap",
        ascending=False
    )
)

print("\n" + "=" * 65)
print("TOP 20 SHAP FEATURES")
print("=" * 65)

print(
    shap_importance
    .head(20)
    .round(6)
    .to_string(index=False)
)


# ============================================================
# 13. CLEAN FEATURE NAMES
# ============================================================

shap_importance["display_feature"] = (
    shap_importance["feature"]
    .str.replace(
        "numeric__",
        "",
        regex=False
    )
    .str.replace(
        "categorical__",
        "",
        regex=False
    )
    .str.replace(
        "_",
        " ",
        regex=False
    )
)


# ============================================================
# 14. SAVE SHAP IMPORTANCE
# ============================================================

os.makedirs(
    "data/model_plots",
    exist_ok=True
)

shap_importance.to_csv(
    "data/shap_feature_importance.csv",
    index=False
)


# ============================================================
# 15. SHAP BAR CHART
# ============================================================

top_features = (
    shap_importance
    .head(20)
    .sort_values(
        "mean_abs_shap",
        ascending=True
    )
)

plt.figure(
    figsize=(10, 8)
)

plt.barh(
    top_features["display_feature"],
    top_features["mean_abs_shap"]
)

plt.xlabel(
    "Mean Absolute SHAP Value"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "SHAP Feature Importance - Customer Churn"
)

plt.tight_layout()

shap_bar_path = (
    "data/model_plots/"
    "shap_feature_importance.png"
)

plt.savefig(
    shap_bar_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"\nSHAP bar chart saved to: {shap_bar_path}"
)


# ============================================================
# 16. SHAP BEESWARM PLOT
# ============================================================

plt.figure(
    figsize=(10, 8)
)

shap.summary_plot(
    shap_churn,
    X_sample,
    feature_names=feature_names,
    max_display=20,
    show=False
)

plt.title(
    "SHAP Summary - Customer Churn Prediction"
)

plt.tight_layout()

shap_beeswarm_path = (
    "data/model_plots/"
    "shap_summary_plot.png"
)

plt.savefig(
    shap_beeswarm_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"SHAP summary plot saved to: {shap_beeswarm_path}"
)


# ============================================================
# 17. COMPLETION
# ============================================================

print("\n" + "=" * 65)
print("SHAP EXPLAINABILITY COMPLETED")
print("=" * 65)

print(
    "\nSaved files:"
)

print(
    "data/shap_feature_importance.csv"
)

print(
    "data/model_plots/shap_feature_importance.png"
)

print(
    "data/model_plots/shap_summary_plot.png"
)