"""
train_model.py
--------------
Standalone training script — equivalent to running notebook 04.
Run from project root: python train_model.py

Saves: models/price_model.joblib
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless runs
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ─── Config ──────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
DATA_PATH = Path("data/processed/buyer_eda/screened_listings.csv")
MODEL_DIR  = Path("models")
FIG_DIR    = Path("figures")
MODEL_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(exist_ok=True)

CAT_FEATURES = ["family", "condition", "province"]
NUM_FEATURES = ["year", "odo_km"]
TARGET       = "price_million"


# ─── 1. Load & Filter ─────────────────────────────────────────────────────────
print("1. Loading data …")
raw = pd.read_csv(DATA_PATH)
df  = raw[raw["price_eligible"] == True].copy()
df["price_million"] = df["price_vnd"] / 1_000_000
df = df.rename(columns={"region": "province"})

print(f"   {len(df):,} price-eligible listings.")

model_df = df[["family", "condition", "year", "odo_km", "province", TARGET]].copy()


# ─── 2. Train / Test split ────────────────────────────────────────────────────
print("2. Splitting 80/20 …")
X = model_df.drop(columns=[TARGET])
y = model_df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)
print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")


# ─── 3. Impute odo_km ─────────────────────────────────────────────────────────
print("3. Imputing odo_km …")

def impute_odo(X_tr, X_te):
    X_tr, X_te = X_tr.copy(), X_te.copy()
    # New → 0
    for frame in (X_tr, X_te):
        frame.loc[frame["condition"] == "New", "odo_km"] = (
            frame.loc[frame["condition"] == "New", "odo_km"].fillna(0)
        )
    # Used → median per family (train only)
    used_train = X_tr[X_tr["condition"] == "Used"]
    odo_medians = used_train.groupby("family")["odo_km"].median()
    global_med  = used_train["odo_km"].median()

    def fill_used(row):
        if row["condition"] == "Used" and pd.isna(row["odo_km"]):
            return odo_medians.get(row["family"], global_med)
        return row["odo_km"]

    X_tr["odo_km"] = X_tr.apply(fill_used, axis=1)
    X_te["odo_km"] = X_te.apply(fill_used, axis=1)
    return X_tr, X_te, odo_medians, global_med

X_train_imp, X_test_imp, odo_medians, global_used_odo = impute_odo(X_train, X_test)


# ─── 4. Baseline ─────────────────────────────────────────────────────────────
print("4. Baseline …")
train_family_median = y_train.groupby(X_train_imp["family"]).median()
overall_median = float(y_train.median())

y_pred_baseline = X_test_imp["family"].map(train_family_median).fillna(overall_median)
mae_baseline = mean_absolute_error(y_test, y_pred_baseline)
r2_baseline  = r2_score(y_test, y_pred_baseline)
print(f"   Baseline  MAE={mae_baseline:.2f}  R²={r2_baseline:.4f}")


# ─── 5. Linear Regression ─────────────────────────────────────────────────────
print("5. Linear Regression …")
preprocessor = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
    ("num", "passthrough", NUM_FEATURES),
])
pipe_lr = Pipeline([("pre", preprocessor), ("model", LinearRegression())])
pipe_lr.fit(X_train_imp, y_train)
y_pred_lr = pipe_lr.predict(X_test_imp)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
r2_lr  = r2_score(y_test, y_pred_lr)
print(f"   LinReg    MAE={mae_lr:.2f}  R²={r2_lr:.4f}")


# ─── 6. Random Forest ─────────────────────────────────────────────────────────
print("6. Random Forest …")
pipe_rf = Pipeline([
    ("pre", ColumnTransformer(transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
        ("num", "passthrough", NUM_FEATURES),
    ])),
    ("model", RandomForestRegressor(
        n_estimators=200, max_depth=10, min_samples_leaf=3,
        random_state=RANDOM_STATE, n_jobs=-1,
    )),
])
pipe_rf.fit(X_train_imp, y_train)
y_pred_rf = pipe_rf.predict(X_test_imp)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
r2_rf  = r2_score(y_test, y_pred_rf)
print(f"   RandForest MAE={mae_rf:.2f}  R²={r2_rf:.4f}")


# ─── 7. Results table ─────────────────────────────────────────────────────────
print("\n=== Model Comparison (Test Set) ===")
results = pd.DataFrame({
    "Model":              ["Baseline", "Linear Regression", "Random Forest"],
    "MAE (triệu VNĐ)":   [mae_baseline, mae_lr, mae_rf],
    "R²":                 [r2_baseline,  r2_lr,  r2_rf],
})
print(results.to_string(index=False))

results.to_csv("data/processed/buyer_eda/model_metrics.csv", index=False)

# Determine best model by MAE
maes = [mae_baseline, mae_lr, mae_rf]
best_idx = int(np.argmin(maes))
best_name = ["Baseline", "Linear Regression", "Random Forest"][best_idx]
print(f"\n🏆 Best model: {best_name}  (MAE={maes[best_idx]:.2f})")


# ─── 8. Figures ───────────────────────────────────────────────────────────────
print("7. Saving figures …")

# Comparison bar chart
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
colors = ["#94a3b8", "#3b82f6", "#10b981"]
names  = ["Baseline", "LinReg", "RandForest"]

axes[0].bar(names, [mae_baseline, mae_lr, mae_rf], color=colors)
axes[0].set_title("MAE (lower is better)")
axes[0].set_ylabel("Triệu VNĐ")
for i, v in enumerate([mae_baseline, mae_lr, mae_rf]):
    axes[0].text(i, v + 1, f"{v:.1f}", ha="center", fontweight="bold")

axes[1].bar(names, [r2_baseline, r2_lr, r2_rf], color=colors)
axes[1].set_title("R² (higher is better)")
axes[1].set_ylabel("R²")
for i, v in enumerate([r2_baseline, r2_lr, r2_rf]):
    axes[1].text(i, max(v + 0.01, 0.01), f"{v:.3f}", ha="center", fontweight="bold")

fig.suptitle("Model Comparison — Test Set (20%)", fontweight="bold")
plt.tight_layout()
plt.savefig(FIG_DIR / "model_comparison.png", bbox_inches="tight", dpi=120)
plt.close()

# Pred vs Actual for best model
best_preds = [y_pred_baseline, y_pred_lr, y_pred_rf][best_idx]
best_mae   = maes[best_idx]
best_r2    = [r2_baseline, r2_lr, r2_rf][best_idx]

fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.scatter(y_test, best_preds, alpha=0.5, s=25, c="#3b82f6", edgecolors="white", linewidths=0.4)
lo = min(float(y_test.min()), float(np.min(best_preds))) - 20
hi = max(float(y_test.max()), float(np.max(best_preds))) + 20
ax2.plot([lo, hi], [lo, hi], "r--", linewidth=1.5, label="y = x")
ax2.set_xlabel("Actual Price (triệu VNĐ)")
ax2.set_ylabel("Predicted Price (triệu VNĐ)")
ax2.set_title(f"Predicted vs. Actual — {best_name}\nMAE={best_mae:.1f}  R²={best_r2:.3f}", fontweight="bold")
ax2.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "pred_vs_actual.png", bbox_inches="tight", dpi=120)
plt.close()
print("   Figures saved to figures/")


# ─── 9. Save model package ───────────────────────────────────────────────────
print("8. Saving model package …")

# Always save the RF pipeline for the app (even if baseline wins on this dataset)
save_pipe = pipe_rf

model_package = {
    "pipeline":               save_pipe,
    "odo_medians_used":       odo_medians.to_dict(),
    "global_used_odo_median": float(global_used_odo) if not np.isnan(global_used_odo) else 30000.0,
    "family_price_medians":   train_family_median.to_dict(),
    "overall_median":         overall_median,
    "cat_features":           CAT_FEATURES,
    "num_features":           NUM_FEATURES,
    "best_model_name":        best_name,
    "metrics": {
        "baseline":          {"mae": mae_baseline, "r2": r2_baseline},
        "linear_regression": {"mae": mae_lr,       "r2": r2_lr},
        "random_forest":     {"mae": mae_rf,        "r2": r2_rf},
    },
    # Test set predictions for Streamlit Model Performance page
    "y_test":          y_test.values.tolist(),
    "y_pred_best":     pipe_rf.predict(X_test_imp).tolist(),
    "y_pred_lr":       y_pred_lr.tolist(),
    "y_pred_rf":       y_pred_rf.tolist(),
    "y_pred_baseline": y_pred_baseline.tolist(),
}

model_path = MODEL_DIR / "price_model.joblib"
joblib.dump(model_package, model_path)
size_kb = model_path.stat().st_size / 1024
print(f"   Saved to {model_path}  ({size_kb:.1f} KB)")

print("\n✅ Training complete!")
print(f"   Best model : {best_name}")
print(f"   MAE        : {maes[best_idx]:.2f} triệu VNĐ")
print(f"   R²         : {[r2_baseline, r2_lr, r2_rf][best_idx]:.4f}")
print("\nRun the app with:")
print("   streamlit run app.py")
