"""
app/data_loader.py
------------------
Utility functions for loading and preparing data used across all Streamlit pages.
Uses st.cache_data so data is only read once per session.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "buyer_eda" / "screened_listings.csv"


@st.cache_data(show_spinner=False)
def load_screened_listings() -> pd.DataFrame:
    """Load the full screened_listings CSV and return the price-eligible cohort."""
    df = pd.read_csv(DATA_PATH)
    eligible = df[df["price_eligible"] == True].copy()
    eligible["price_million"] = eligible["price_vnd"] / 1_000_000
    # Rename region → province for clarity
    eligible = eligible.rename(columns={"region": "province"})
    return eligible


def get_families(df: pd.DataFrame) -> list[str]:
    """Return sorted list of VinFast families present in the data."""
    return sorted(df["family"].dropna().unique().tolist())


def get_provinces(df: pd.DataFrame) -> list[str]:
    """Return sorted list of provinces present in the data."""
    return sorted(df["province"].dropna().unique().tolist())


def get_conditions() -> list[str]:
    return ["New", "Used"]
