"""
app/model_loader.py
-------------------
Load the trained price-prediction pipeline saved by notebook 04.
Caches it for the lifetime of the Streamlit session.
"""

from pathlib import Path
import streamlit as st
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = Path(__file__).parent.parent / "models" / "price_model.joblib"


@st.cache_resource(show_spinner=False)
def load_model_package() -> dict:
    """Load and return the full model package dict saved by the notebook."""
    if not MODEL_PATH.exists():
        st.error("⚠️ Chưa tìm thấy file mô hình. Hãy chạy notebook 04 trước.")
        st.stop()
    return joblib.load(MODEL_PATH)


def predict_price(
    model_package: dict,
    family: str,
    condition: str,
    year: int,
    odo_km: float,
    province: str,
) -> tuple[float, float]:
    """
    Predict price in triệu VNĐ for given inputs.
    Returns (predicted_price, family_median_price).
    """
    pipeline = model_package["pipeline"]
    odo_medians = model_package["odo_medians_used"]
    global_used_odo = model_package["global_used_odo_median"]
    family_medians = model_package["family_price_medians"]
    overall_median = model_package["overall_median"]

    # Handle odo_km imputation matching notebook logic
    if condition == "New":
        odo_filled = 0.0 if (odo_km is None or np.isnan(odo_km)) else odo_km
    else:
        if odo_km is None or np.isnan(odo_km):
            odo_filled = odo_medians.get(family, global_used_odo)
        else:
            odo_filled = odo_km

    row = pd.DataFrame(
        [{"family": family, "condition": condition, "year": year,
          "odo_km": odo_filled, "province": province}]
    )

    predicted = float(pipeline.predict(row)[0])
    family_median = family_medians.get(family, overall_median)

    return predicted, family_median
