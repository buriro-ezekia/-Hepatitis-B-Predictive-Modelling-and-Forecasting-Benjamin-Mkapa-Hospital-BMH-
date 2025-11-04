# Hepatitis B Predictive Modelling and Forecasting – Benjamin Mkapa Hospital (BMH)

## Project Overview

This repository contains the data analysis and predictive modelling components of a longitudinal study on **Hepatitis B patient trends** conducted at **Benjamin Mkapa Hospital (BMH)**, Dodoma, Tanzania.  
The project applies **machine learning techniques** to hospital records from **2017–2024** to identify temporal patterns, build predictive models, and forecast patient numbers for the next five years (2025–2029).

The analysis supports strategic healthcare planning by providing evidence-based insights into patient growth, diagnostic trends, and resource demand forecasting.

---

## Research Objectives

1. **Analyse Hepatitis B patient trends** at BMH using longitudinal hospital data.  
2. **Develop predictive models** to estimate patient growth and clinic attendance patterns.  
3. **Forecast Hepatitis B patient numbers** for 2025–2029 using the most accurate model.

---

## Analytical Workflow

### 1. Data Preparation
- Dataset: 1,710 longitudinal patient records (2017–2024)
- Features: Age, Gender, Viral Load, ALT Level, Follow-up Duration, LTFU status, and Registration Date  
- Cleaning: Duplicate removal, missing value handling, date conversions, and standardisation  
- Split: 80% training / 20% testing (chronological order)

### 2. Exploratory Analysis
- Trend assessment of patient counts by year and month  
- Lost-to-Follow-Up (LTFU) distribution  
- Seasonal and demographic analysis  
- Visualization of follow-up duration and patient inflow

### 3. Model Development
Four supervised learning algorithms were developed and tuned:

| Model | Framework | Key Features | Strengths |
|-------|------------|---------------|------------|
| **Linear Regression** | Scikit-learn | Baseline statistical model | High interpretability |
| **XGBoost** | XGBoost | Ensemble gradient boosting | Handles feature interaction |
| **LightGBM** | LightGBM | Leaf-wise boosting | Faster computation |
| **LSTM (RNN)** | TensorFlow / Keras | Sequential modelling | Captures temporal dependencies |

All models were trained to predict monthly patient counts using temporal and clinical variables.

---

## Model Evaluation

Performance was assessed on the test dataset using the following metrics:

| Model | MSE | RMSE | MAE | MAPE (%) | Remarks |
|--------|------|------|------|-----------|----------|
| **Linear Regression** | **527.09** | **22.96** | **18.52** | **33.81** | *Best overall performance* |
| XGBoost | 762.65 | 27.62 | 23.14 | 39.22 | Slight overfit |
| LightGBM | 788.45 | 28.08 | 23.71 | 39.99 | Comparable to XGBoost |
| LSTM (RNN) | ~1635.0 | ~40.43 | ~32.15 | ~48.00 | Less stable on small dataset |

**Result:**  
The **Linear Regression model** achieved the best predictive accuracy, confirming that the underlying trend in Hepatitis B cases is primarily linear over time.

---

## Forecasting Results (2025–2029)

Forecasts were generated using the best-performing model (Linear Regression):

| Year | Predicted Monthly Average | Lower 95% CI | Upper 95% CI |
|------|----------------------------|---------------|---------------|
| 2025 | 468 | 398 | 538 |
| 2026 | 512 | 432 | 593 |
| 2027 | 555 | 462 | 648 |
| 2028 | 601 | 495 | 707 |
| 2029 | 648 | 525 | 771 |

**Insight:**  
A projected **8–9% annual increase** in Hepatitis B cases suggests rising healthcare demand and diagnostic throughput at BMH.

---

## Tools and Libraries

- **Python 3.10+**
- **NumPy**, **Pandas**, **Matplotlib**
- **Scikit-learn**
- **XGBoost**
- **LightGBM**
- **TensorFlow / Keras**

---

## 📂 Repository Structure

