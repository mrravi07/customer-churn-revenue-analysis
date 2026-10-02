# ============================================================
# CUSTOMER CHURN & REVENUE ANALYSIS
# FEATURE IMPORTANCE VISUALIZATION
# ============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 01. LOAD FEATURE IMPORTANCE
# ============================================================

INPUT_PATH = "data/feature_importance_v2.csv"

print("\nLoading feature importance...")

df = pd.read_csv(INPUT_PATH)

print(f"Features loaded: {len(df):,}")


# ============================================================
# 02. CLEAN FEATURE NAMES
# ============================================================

df["feature"] = (
    df["feature"]
    .str.replace("numeric__", "", regex=False)
    .str.replace("categorical__", "", regex=False)
    .str.replace("_", " ", regex=False)
)


# ============================================================
# 03. SORT TOP FEATURES
# ============================================================

df = (
    df.sort_values(
        "importance",
        ascending=True
    )
)


# ============================================================
# 04. CREATE OUTPUT DIRECTORY
# ============================================================

output_dir = "data/model_plots"

os.makedirs(
    output_dir,
    exist_ok=True
)


# ============================================================
# 05. FEATURE IMPORTANCE CHART
# ============================================================

plt.figure(
    figsize=(10, 8)
)

plt.barh(
    df["feature"],
    df["importance"]
)

plt.xlabel(
    "Feature Importance"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "Top 20 Random Forest Features - Customer Churn"
)

plt.tight_layout()


output_path = (
    f"{output_dir}/"
    "random_forest_feature_importance.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


print(
    f"\nFeature importance chart saved to: {output_path}"
)


# ============================================================
# 06. DISPLAY TOP FEATURES
# ============================================================

print("\n" + "=" * 65)
print("TOP 20 FEATURES")
print("=" * 65)

display_df = (
    df.sort_values(
        "importance",
        ascending=False
    )
    .copy()
)

display_df["importance"] = (
    display_df["importance"]
    .round(4)
)

print(
    display_df.to_string(
        index=False
    )
)


# ============================================================
# 07. COMPLETION
# ============================================================

print("\n" + "=" * 65)
print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
print("=" * 65)