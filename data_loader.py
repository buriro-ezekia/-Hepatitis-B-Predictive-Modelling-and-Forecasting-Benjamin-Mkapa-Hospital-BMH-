"""
Small helper for loading and validating forecast & patient CSVs.
Intended to be imported from app.py. Uses pandas and numpy only.
"""

from typing import Optional
import os
import io
import pandas as pd
import numpy as np
import streamlit as st

REQUIRED_FORECAST_COLS = {"date", "predicted_median"}
OPTIONAL_PI_COLS = {"pi80_low", "pi80_high", "pi95_low", "pi95_high", "actual"}

@st.cache_data(ttl=300)
def load_forecast_csv_path(path: str, anonymize: bool = False) -> pd.DataFrame:
    """Load and normalize a forecast CSV on disk (path)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Forecast CSV not found: {path}")
    df = pd.read_csv(path, parse_dates=["date"])
    return _normalize_forecast_df(df, anonymize=anonymize)

@st.cache_data(ttl=300)
def load_forecast_filelike(file_like: io.BytesIO, anonymize: bool = False) -> pd.DataFrame:
    """Load and normalize a forecast CSV from an uploaded file (BytesIO)."""
    df = pd.read_csv(file_like, parse_dates=["date"])
    return _normalize_forecast_df(df, anonymize=anonymize)

def _normalize_forecast_df(df: pd.DataFrame, anonymize: bool = False) -> pd.DataFrame:
    """Ensure required columns, add safe defaults for optional columns, and return sorted df."""
    # Normalize column names
    df = df.rename(columns=lambda c: c.strip())
    cols = set(df.columns)

    missing = REQUIRED_FORECAST_COLS - cols
    if missing:
        raise ValueError(f"Missing required columns in forecast CSV: {sorted(missing)}")

    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    # Add optional columns if missing
    if "actual" not in df.columns:
        df["actual"] = np.nan
    if not ({"pi80_low","pi80_high"} <= set(df.columns)):
        pi80 = 1.5
        df["pi80_low"] = df["predicted_median"] - pi80
        df["pi80_high"] = df["predicted_median"] + pi80
    if not ({"pi95_low","pi95_high"} <= set(df.columns)):
        pi95 = 3.0
        df["pi95_low"] = df["predicted_median"] - pi95
        df["pi95_high"] = df["predicted_median"] + pi95

    # Optional anonymization placeholder
    if anonymize and "patient_id" in df.columns:
        df["patient_id"] = df["patient_id"].apply(lambda v: f"anon_{abs(hash(str(v)))%10_000_000}")

    return df

def load_patient_csv_path(path: str, anonymize: bool = True) -> pd.DataFrame:
    """Load patient CSV and optionally anonymize sensitive columns."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Patient CSV not found: {path}")
    df = pd.read_csv(path, parse_dates=True)
    return _normalize_patient_df(df, anonymize=anonymize)

def _normalize_patient_df(df: pd.DataFrame, anonymize: bool = True) -> pd.DataFrame:
    df = df.copy()
    # Basic parse of dates if present
    for c in df.columns:
        if "date" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                pass
    if anonymize:
        # Remove or hash common PHI columns if present
        for phi in ("name","email","phone","ssn","mrn"):
            if phi in df.columns:
                df[phi] = df[phi].apply(lambda v: None)
        if "patient_id" in df.columns:
            df["patient_hash"] = df["patient_id"].apply(lambda v: f"sha256:{abs(hash(str(v)))%10_000_000}")
            df = df.drop(columns=["patient_id"])
    return df
