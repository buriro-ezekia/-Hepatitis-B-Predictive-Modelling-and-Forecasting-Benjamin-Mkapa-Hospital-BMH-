import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Hepatitis B Forecasting")

# --- Simulated data generation ---
def gen_forecast_data(start_date, days=60, horizon=14):
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

# --- Data ---
df_forecast = gen_forecast_data(start_date, days=60, horizon=horizon)
df_metrics = gen_metrics(df_forecast)
df_patients = gen_patient_table(100)

# --- Header ---
col1, col2, col3 = st.columns([3,1,1])
with col1:
    st.title("Hepatitis B Forecasting — BMH")
    st.markdown(f"Model: **{model_version}** • Last run: {datetime.now().isoformat(timespec='seconds')}")
with col2:
    st.metric("Next-7-day expected cases", int(df_forecast['predicted_median'][-7:].sum()), delta="+4%")
with col3:
    st.metric("Model confidence", "82%", delta="-1%")

# --- Forecast chart + KPIs ---
left, right = st.columns([3,1])
with left:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_forecast.date, y=df_forecast.actual, mode="lines+markers", name="Actual"))
    fig.add_trace(go.Scatter(x=df_forecast.date, y=df_forecast.predicted_median, mode="lines", name="Predicted"))
    fig.add_trace(go.Scatter(x=df_forecast.date, y=df_forecast.pi95_high, fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
    fig.add_trace(go.Scatter(
        x=df_forecast.date.tolist()+df_forecast.date[::-1].tolist(),
        y=df_forecast.pi80_high.tolist()+df_forecast.pi80_low[::-1].tolist(),
        fill='toself',
        fillcolor='rgba(0,176,246,0.1)',
        line_color='rgba(255,255,255,0)',
        name='80% PI',
        showlegend=True
    ))
    fig.update_layout(height=420, margin=dict(l=10,r=10,t=30,b=10), legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Quick KPIs")
    st.metric("MAE (7d)", f"{df_metrics.MAE.iloc[-1]:.2f}")
    st.metric("RMSE (7d)", f"{df_metrics.RMSE.iloc[-1]:.2f}")
    drift_score = np.round(np.random.rand(), 2)
    st.metric("Data drift score", f"{drift_score}", delta="+0.02")

# --- Performance & Data Quality ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Model performance (rolling 7d)")
    fig2 = px.line(df_metrics, x="date", y=["MAE","RMSE"])
    st.plotly_chart(fig2, use_container_width=True)
with c2:
    st.subheader("Data quality — missingness (simulated)")
    # Simulated heatmap
    features = ["ALT","AST","HBsAg","Platelets","Age"]
    mat = np.random.rand(len(features), 30)
    df_heat = pd.DataFrame(mat, index=features, columns=pd.date_range(datetime.now()-timedelta(days=29), periods=30).strftime("%Y-%m-%d"))
    st.dataframe(df_heat.style.background_gradient(axis=None))

# --- Alerts & Logs ---
a1, a2 = st.columns([1,3])
with a1:
    st.subheader("Alerts")
    st.info("Accuracy drop > 15% in last 7 days")
    st.warning("Feature 'HBsAg' missing rate > 20% on recent batch")
with a2:
    st.subheader("Recent retrain & audit log")
    st.write("- v1.1 retrain finished 2025-11-10 03:20 (commit: abcd1234)")
    st.write("- Manual review: cohort filter adjusted (Adults 46+)")
    st.button("Trigger retrain (demo)")

# --- Patient table ---
st.subheader("Patient-level explorer")
st.write("Click a row to view details (demo table with hashed ids).")
st.dataframe(df_patients.head(30))

# # --- Footer / notes ---
# st.markdown("---")
# st.caption("Prototype uses simulated data. Next step: hook to real /api endpoints and add auth, RBAC, and alert integrations.")
