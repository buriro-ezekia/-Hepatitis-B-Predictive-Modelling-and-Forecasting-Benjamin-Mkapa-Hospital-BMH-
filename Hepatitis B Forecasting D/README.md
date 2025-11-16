```markdown
# Hepatitis B Forecasting Dashboard

Overview
- Purpose: Provide clinicians and hospital admins with an at-a-glance view of forecasts, model health, and data quality for Hepatitis B cases. Support drill-down to cohort and patient-level detail for triage and auditing.
- Target users: clinicians, epidemiologists, data scientists, hospital admins.
- Goals: show forecasts + uncertainty, monitor model performance and drift, surface alerts, and enable investigation.

Top-level layout (responsive, desktop first)
- Header (full width, 80–100px)
  - Left: Project title (Hepatitis B Forecasting — BMH)
  - Center: model version badge, last run timestamp, data snapshot info
  - Right: user avatar, quick actions (retrain, export, settings)

- Left Sidebar (collapsible, 220px)
  - Navigation tabs: Overview (default), Forecasts, Model Health, Data Quality, Patient Explorer, Audit Logs
  - Quick filters (persistent): facility/ward, cohort (age groups), forecast horizon selector (7/14/30 days)
  - Alerts summary (small badges)

- Main area (grid: 2 columns on desktop)
  - Row A (full-width or left-large + right-small)
    - Left (primary): Forecast chart (line + CI bands), timeline scrubber, forecast scenarios toggle (model A / model B)
    - Right (narrow): KPI cards (numeric KPIs)
      - Next-7-day expected cases, change vs prev week (%), current anomaly score, model confidence index
  - Row B (two columns)
    - Left: Accuracy & performance over time chart (MAE/RMSE/MAPE) with model selector
    - Right: Model comparison small multiples + variable importance snapshot for selected model
  - Row C (two columns)
    - Left: Data quality panel: missingness heatmap, feature drift sparkline, distribution shift warnings
    - Right: Alerts feed + recent retrain activity + one-click retrain (with confirmation)
  - Row D (full width)
    - Patient-level explorer: table with filters and drill-in; columns: patient_id (hashed), date, predicted_risk, probability, top contributing features, cohort tags, action button (annotate)
    - Export buttons, pagination, and download CSV

- Footer (small): links to docs, privacy/policy, dataset snapshots.

Components — details
- Forecast chart
  - Time series line for actuals and predicted median
  - Shaded band for 80% & 95% prediction intervals
  - Hover: show numeric values + last-run commit id + input snapshot
  - Controls: change horizon, show confidence bands, overlay actuals (toggle)
- KPI cards
  - Value, small sparkline (past 14 days), delta vs previous period, tooltip with calculation
- Accuracy chart
  - Time (x) vs MAE/RMSE/MAPE (y), choose metric(s), annotate retrain events
- Data quality
  - Missingness heatmap (features vs time), row-level sample, drift score per feature (0-1)
- Alerts
  - Thresholded alerts for accuracy drop, sudden case surge, unusual missingness, model drift
  - Each alert links to relevant panel and provides suggested actions
- Patient-table & drill-in
  - Row click opens sidebar with feature contributions, input snapshot, audit trail (model version, inference timestamp)
  - Privacy: hashed IDs, configurable anonymization, access control roles

Interactions & UX
- Cross-filtering: selecting date range or cohort updates all panels
- Drill-in: charts allow selecting a window and opening patient-level results filtered to that window
- Save bookmarks: URL state includes filters and model version
- Notifications: email/Slack integration for critical alerts
- Mobile: condensed stack — header + KPIs + small chart + critical alerts + compact table

Color & accessibility
- Use colorblind-safe palette (e.g., Viridis or Tableau 10)
- Contrast ratio >4.5 for text on background
- All charts have accessible descriptions and keyboard navigation where feasible

Data & API requirements (example endpoints)
- GET /api/forecasts?start=YYYY-MM-DD&end=YYYY-MM-DD&horizon=7&model=baseline
  - returns: { dates: [...], predicted_median: [...], pi80_low: [...], pi80_high: [...], pi95_low: [...], pi95_high: [...] }
- GET /api/metrics?metric=MAE&group_by=week&model=baseline
  - returns: [{ period_start, MAE, RMSE, MAPE, model_version }]
- GET /api/data-quality?start=&end=
  - returns: { feature_stats: [{name, missing_rate_over_time: [...], drift_score}], missingness_matrix: [[...]] }
- GET /api/predictions?start=&end=&cohort=&limit=50
  - returns list of prediction objects: {patient_id_hashed, date, predicted_risk, probability, top_features: [{name, contribution}], model_version, inference_time}
- POST /api/retrain (protected)
  - input: model config / training window
  - response: job id

Data schema examples
- Forecast point:
  - { date: "2025-11-01", actual: 12, predicted_median: 14.2, pi80_low: 11.1, pi80_high: 17.3, pi95_low: 9.8, pi95_high: 19.6 }
- Metric sample:
  - { period_start: "2025-10-01", MAE: 1.7, RMSE: 2.1, MAPE: 0.12, model_version: "v1.3-commit-abcd" }
- Prediction row:
  - { patient_hash: "sha256:xxxx", date: "2025-11-02", predicted_risk: "high", probability: 0.86, top_features: [{"ALT":0.21}, {"HBsAg":0.18}] }

Telemetry, logs & lineage
- Store model version (git commit), training dataset snapshot id, config used, and last trained timestamp with every reported metric and prediction.
- Audit trail for patient-level queries (who viewed what and when).

Performance & infra notes
- Use TimescaleDB/Influx for time-series metrics + Postgres for relational patient metadata.
- Cache recent forecasts in Redis for fast retrieval.
- Use a job orchestration tool (Prefect/Airflow) for scheduled inference + metric aggregation.

Prototype considerations
- Rapid prototyping: Streamlit or Plotly Dash.
- Production UI: React + Plotly/D3; backend: FastAPI; DB: Postgres + Timescale; auth: OAuth/OIDC + RBAC.

Acceptance criteria / definition of done (first milestone)
- Live dashboard shows latest forecast + CI for selected horizon
- Accuracy chart with at least MAE and RMSE plotted
- Data-quality panel shows missingness and drift for key features
- Patient explorer returns sample predictions with top-feature contributions
- Alerts for model accuracy drop configured (email/Slack)

Security & privacy
- Hash patient identifiers and allow toggling of de-anonymization under strict ACL
- Ensure all exported reports exclude PII unless user is authorized
```
