import os
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Hepatitis B Forecasting")

# Try to use centralized data_loader if present, otherwise fall back to built-in loaders
try:
    from data_loader import load_forecast_csv_path, load_forecast_filelike
    HAS_DATA_LOADER = True
except Exception:
    HAS_DATA_LOADER = False

    def _normalize_forecast_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=lambda c: c.strip())
        if "date" not in df.columns:
            raise ValueError("No 'date' column found in forecast CSV.")
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        if "predicted_median" not in df.columns:
            raise ValueError("Missing required column 'predicted_median'.")
        if "actual" not in df.columns:
            df["actual"] = np.nan
        if not ({"pi80_low", "pi80_high"} <= set(df.columns)):
            pi80 = 1.5
            df["pi80_low"] = df["predicted_median"] - pi80
            df["pi80_high"] = df["predicted_median"] + pi80
        if not ({"pi95_low", "pi95_high"} <= set(df.columns)):
            pi95 = 3.0
            df["pi95_low"] = df["predicted_median"] - pi95
            df["pi95_high"] = df["predicted_median"] + pi95
        return df

    def load_forecast_csv_path(path: str) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=["date"], low_memory=False)
        return _normalize_forecast_df(df)

    def load_forecast_filelike(fobj: io.BytesIO) -> pd.DataFrame:
        df = pd.read_csv(fobj, parse_dates=["date"])
        return _normalize_forecast_df(df)


# --- Data loaders / generators / specialized parsers ---

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

# Specialized loader for monthly_forecast_2025_2029.csv
def load_monthly_forecast(path: str) -> pd.DataFrame:
    """
    Load monthly_forecast_2025_2029.csv and normalize to columns:
      - date (datetime, first of month)
      - predicted_median (numeric)
      - optional: actual, pi80_low/high, pi95_low/high
    The function will try to autodetect date-like and numeric columns and let the user confirm via sidebar if multiple choices exist.
    """
    df = pd.read_csv(path, low_memory=False)
    # Detect date-like columns and numeric columns
    date_like = [c for c in df.columns if any(k in c.lower() for k in ("date","month","period","year"))]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Also include numeric-like columns that may be strings
    numeric_like = [c for c in df.columns if c not in numeric_cols and df[c].astype(str).str.replace(r'[^\d\.\-]', '', regex=True).str.len().gt(0).any()]

    # Provide feedback in sidebar and allow user mapping
    st.sidebar.markdown("### monthly_forecast_2025_2029.csv detected columns")
    st.sidebar.write(f"Date-like columns: {date_like or 'none detected'}")
    st.sidebar.write(f"Numeric columns: {numeric_cols or 'none detected'}")
    # Let user pick date column
    if date_like:
        date_col = st.sidebar.selectbox("Select date/month column", date_like, index=0)
    else:
        # fallback: choose the first column or ask user
        date_col = st.sidebar.selectbox("Select date/month column (no obvious candidate)", df.columns.tolist(), index=0)
    # Let user pick value column (prefer names containing 'forecast','pred','median','value','count','cases')
    preferred = [c for c in (numeric_cols + numeric_like) if any(k in c.lower() for k in ("forecast","pred","median","value","count","case","cases","n_","total"))]
    candidate_value_cols = preferred or (numeric_cols + numeric_like)
    if not candidate_value_cols:
        raise ValueError("No numeric columns found to use as predicted_median.")
    value_col = st.sidebar.selectbox("Select value column to use as predicted_median", candidate_value_cols, index=0)

    # Parse dates: if entries look like YYYY-MM, append -01
    series = pd.to_datetime(df[date_col], errors="coerce")
    if series.isna().all():
        # try adding day=1 to year-month strings
        series = pd.to_datetime(df[date_col].astype(str).str.strip() + "-01", errors="coerce")
    # final fallback: use index with monthly spacing starting from today - len
    if series.isna().any():
        # try resilient parsing: coerce and drop NA rows later
        series = pd.to_datetime(df[date_col], errors="coerce")

    out = pd.DataFrame({
        "date": series,
        "predicted_median": pd.to_numeric(df[value_col], errors="coerce")
    })

    # Optional actual detection
    possible_actual = [c for c in df.columns if any(k in c.lower() for k in ("actual","observed","obs","report"))]
    if possible_actual:
        out["actual"] = pd.to_numeric(df[possible_actual[0]], errors="coerce")
    else:
        out["actual"] = np.nan

    # Add simple PIs if not present in original file
    if "pi80_low" not in out.columns:
        sigma = out["predicted_median"].std(skipna=True)
        pi80 = sigma if not np.isnan(sigma) and sigma > 0 else 1.5
        out["pi80_low"] = out["predicted_median"] - pi80
        out["pi80_high"] = out["predicted_median"] + pi80
    if "pi95_low" not in out.columns:
        sigma = out["predicted_median"].std(skipna=True)
        pi95 = 2 * (sigma if not np.isnan(sigma) and sigma > 0 else 3.0)
        out["pi95_low"] = out["predicted_median"] - pi95
        out["pi95_high"] = out["predicted_median"] + pi95

    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return out

# --- UI Controls ---
st.sidebar.title("Controls")
horizon = st.sidebar.selectbox("Forecast horizon (days)", [7, 14, 30], index=1)
cohort = st.sidebar.selectbox("Cohort", ["All", "Adults 18-45", "Adults 46+", "Pediatrics"], index=0)
model_version = st.sidebar.selectbox("Model version", ["v1.0", "v1.1", "experimental"], index=1)
start_date = datetime.now().date()

# Data source selection
st.sidebar.markdown("### Forecast data source")
# default repo CSV path updated per your request
repo_csv_path = "data/monthly_forecast_2025_2029.csv"
use_repo_csv = False
if os.path.exists(repo_csv_path):
    use_repo_csv = st.sidebar.checkbox(f"Load {repo_csv_path}", value=True)
else:
    # also offer to try the generic path
    alt_path = "data/forecasts.csv"
    if os.path.exists(alt_path):
        use_repo_csv = st.sidebar.checkbox(f"Load {alt_path}", value=False)
        repo_csv_path = alt_path
    else:
        st.sidebar.write(f"No repo CSV at {repo_csv_path} or {alt_path}")

uploaded_file = st.sidebar.file_uploader("Or upload forecast CSV (monthly)", type=["csv"])

# --- Data Loading (attempt uploaded file, then specialized monthly loader, then generic loader, else fallback) ---
df_forecast = None
load_error = None

if uploaded_file is not None:
    try:
        if HAS_DATA_LOADER:
            df_forecast = load_forecast_filelike(uploaded_file)
        else:
            uploaded_name = getattr(uploaded_file, "name", "").lower()
            uploaded_file.seek(0)
            # if filename suggests monthly forecast, use specialized parser
            if "monthly" in uploaded_name or "forecast" in uploaded_name or "2025" in uploaded_name:
                uploaded_file.seek(0)
                # read into temp file on string IO for the specialized loader
                s = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                df_forecast = load_monthly_forecast(io.StringIO(s))
            else:
                uploaded_file.seek(0)
                df_forecast = load_forecast_filelike(uploaded_file)
    except Exception as e:
        load_error = f"Uploaded CSV error: {e}"
elif use_repo_csv:
    try:
        # If the chosen repo CSV matches the monthly filename, use the specialized loader
        if os.path.basename(repo_csv_path).lower().startswith("monthly") or "monthly" in os.path.basename(repo_csv_path).lower():
            df_forecast = load_monthly_forecast(repo_csv_path)
        else:
            if HAS_DATA_LOADER:
                df_forecast = load_forecast_csv_path(repo_csv_path)
            else:
                df_forecast = load_forecast_csv_path(repo_csv_path)
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
    # PI ribbons (guard against missing values)
    if all(c in df_forecast.columns for c in ("pi95_high","pi95_low")):
        fig.add_traces([
            go.Scatter(
                x=pd.concat([df_forecast["date"], df_forecast["date"][::-1]]),
                y=pd.concat([df_forecast["pi95_high"], df_forecast["pi95_low"][::-1]]),
                fill='toself', fillcolor='rgba(200,200,255,0.2)',
                line=dict(color='rgba(255,255,255,0)'), showlegend=False, name="95% PI"
            )
        ])
    if all(c in df_forecast.columns for c in ("pi80_high","pi80_low")):
        fig.add_traces([
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
    if not df_metrics.empty:
        latest = df_metrics.iloc[-1][["MAE","RMSE"]].to_frame().T
        st.table(latest)
    else:
        st.write("No metrics available")

st.markdown("### Patients (sample)")
st.dataframe(df_patients.head(20))

# Optional: allow downloading a cleaned/validated CSV
if st.button("Download validated forecast CSV"):
    buf = df_forecast.copy()
    buf["date"] = pd.to_datetime(buf["date"]).dt.strftime("%Y-%m-%d")
    csv = buf.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="validated_forecast.csv", mime="text/csv")
