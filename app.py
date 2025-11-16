import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Hepatitis B Forecasting")

# --- Data loaders / generators ---

def gen_forecast_data(start_date, days=60, horizon=14):
    """Fallback simulated data (kept for demo / fallback)."""
    dates = pd.date_range(start_date - pd.Timedelta(days=30), periods=days)
    np.random.seed(42)
    actual = np.clip(np.round(10 + np.sin(np.linspace(0, 3.14, days)) * 4 + np.random.randn(days)), 0, None)
    predicted_median = actual + np.random.normal(0.5, 1.0, size=days)
    pi80 = 1.5
    pi95 = 3.0
    df = pd.DataFrame({
        "date": dates,
        "actual": actual,
        "predicted_median": predicted_median,
        "pi80_low": predicted_median - pi80,
        "pi80_high": predicted_median + pi80,
        "pi95_low": predicted_median - pi95,
        "pi95_high": predicted_median + pi95,
    })
    return df

def load_forecast_csv(path="data/forecasts.csv"):
    """
    Load a forecast CSV and validate minimal columns.
    Expected minimal columns: date, predicted_median
    Optional: actual, pi80_low/pi80_high, pi95_low/pi95_high
    """
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # ensure required columns
    expected = ["date", "predicted_median"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in forecast CSV: {missing}")

    # normalize column names (strip)
    df.columns = [c.strip() for c in df.columns]

    # Add optional columns if missing so the rest of the app can assume they exist
    if "actual" not in df.columns:
        df["actual"] = np.nan
    if "pi80_low" not in df.columns or "pi80_high" not in df.columns:
        # create simple fixed-width PI if not provided (safe fallback)
        pi80 = 1.5
        df["pi80_low"] = df["predicted_median"] - pi80
        df["pi80_high"] = df["predicted_median"] + pi80
    if "pi95_low" not in df.columns or "pi95_high" not in df.columns:
        pi95 = 3.0
        df["pi95_low"] = df["predicted_median"] - pi95
        df["pi95_high"] = df["predicted_median"] + pi95

    return df

def gen_metrics(df):
    df_metrics = df.copy()
    # If actuals are not available, error-based metrics will be NaN
    df_metrics["error"] = (df_metrics["actual"] - df_metrics["predicted_median"]).abs()
    df_metrics["MAE"] = df_metrics["error"].rolling(7, min_periods=1).mean()
    df_metrics["RMSE"] = np.sqrt((df_metrics["error"]**2).rolling(7, min_periods=1).mean())
    return df_metrics

def gen_patient_table(n=50):
    np.random.seed(1)
    base = []
    for i in range(n):
        date = datetime.now().date() - timedelta(days=np.random.randint(0,14))
        prob = np.round(np.random.beta(2,5), 2)
        base.append({
            "patient_hash": f"sha256:{np.random.randint(10**8)}",
            "date": date.isoformat(),
            "predicted_risk": "high" if prob > 0.7 else ("medium" if prob>0.4 else "low"),
            "probability": prob,
            "top_feature_1": np.random.choice(["ALT","AST","HBsAg","Age","Platelets"]),
            "top_feature_2": np.random.choice(["ALT","AST","HBsAg","Age","Platelets"]),
        })
    return pd.DataFrame(base)

# --- UI Controls ---
st.sidebar.title("Controls")
horizon = st.sidebar.selectbox("Forecast horizon (days)", [7, 14, 30], index=1)
cohort = st.sidebar.selectbox("Cohort", ["All", "Adults 18-45", "Adults 46+", "Pediatrics"], index=0)
model_version = st.sidebar.selectbox("Model version", ["v1.0", "v1.1", "experimental"], index=1)
start_date = datetime.now().date()

# Data source selection
st.sidebar.markdown("### Forecast data source")
use_repo_csv = False
repo_csv_path = "data/forecasts.csv"
if os.path.exists(repo_csv_path):
    use_repo_csv = st.sidebar.checkbox(f"Load {repo_csv_path}", value=True)
else:
    st.sidebar.write(f"No repo CSV at {repo_csv_path}")

uploaded_file = st.sidebar.file_uploader("Or upload forecast CSV", type=["csv"])

# --- Data Loading (attempt CSV, then uploaded file, else fallback to simulated) ---
df_forecast = None
load_error = None

if uploaded_file is not None:
    try:
        df_forecast = pd.read_csv(uploaded_file, parse_dates=["date"])
        df_forecast = df_forecast.sort_values("date").reset_index(drop=True)
        # Validate minimal columns
        if "predicted_median" not in df_forecast.columns:
            load_error = "Uploaded CSV is missing the required column: predicted_median"
    except Exception as e:
        load_error = f"Error reading uploaded CSV: {e}"
elif use_repo_csv:
    try:
        df_forecast = load_forecast_csv(repo_csv_path)
    except Exception as e:
        load_error = f"Error loading {repo_csv_path}: {e}"

if df_forecast is None:
    if load_error:
        st.sidebar.error(load_error)
        st.sidebar.info("Falling back to simulated demo data.")
    df_forecast = gen_forecast_data(start_date, days=60, horizon=horizon)

# --- Derived data ---
df_metrics = gen_metrics(df_forecast)
df_patients = gen_patient_table(100)

# --- Simple dashboard display (examples) ---
st.title("Hepatitis B Forecasting Dashboard")

col1, col2 = st.columns([3,1])

with col1:
    st.subheader("Forecast over time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_forecast["date"], y=df_forecast["predicted_median"],
        mode="lines+markers", name="Predicted median"
    ))
    if "actual" in df_forecast.columns and df_forecast["actual"].notna().any():
        fig.add_trace(go.Scatter(
            x=df_forecast["date"], y=df_forecast["actual"],
            mode="lines+markers", name="Actual"
        ))
    # PI ribbons
    fig.add_traces([
        go.Scatter(
            x=pd.concat([df_forecast["date"], df_forecast["date"][::-1]]),
            y=pd.concat([df_forecast["pi95_high"], df_forecast["pi95_low"][::-1]]),
            fill='toself', fillcolor='rgba(200,200,255,0.2)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False, name="95% PI"
        ),
        go.Scatter(
            x=pd.concat([df_forecast["date"], df_forecast["date"][::-1]]),
            y=pd.concat([df_forecast["pi80_high"], df_forecast["pi80_low"][::-1]]),
            fill='toself', fillcolor='rgba(150,150,255,0.4)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False, name="80% PI"
        )
    ])
    fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Count / Score")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Latest metrics")
    latest = df_metrics.iloc[-1][["MAE","RMSE"]].to_frame().T
    st.table(latest)

st.markdown("### Patients (sample)")
st.dataframe(df_patients.head(20))

# Optional: allow downloading a cleaned/validated CSV
if st.button("Download validated forecast CSV"):
    buf = df_forecast.copy()
    buf["date"] = buf["date"].dt.strftime("%Y-%m-%d")
    csv = buf.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="validated_forecast.csv", mime="text/csv")
