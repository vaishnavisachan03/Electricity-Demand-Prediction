# Delhi Power-Demand Prediction System
An AI-powered short-term electricity demand forecasting system designed to help Delhi's power-grid operators anticipate demand, identify high-risk periods, and make better decisions for grid management. 

## Problem Statement
Delhi experiences significant variations in electricity demand, especially during extreme summer temperatures. Accurate short-term demand forecasting can help power distribution companies and grid operators prepare for demand peaks, maintain sufficient reserves, and reduce the risk of grid stress.
Our system uses historical weather patterns, temporal information, and previous electricity demand to forecast electricity demand for the upcoming hours.

## Solution
We developed an AI-based forecasting pipeline that:
- Uses historical Delhi weather observations.
- Engineers time-based and temperature-based features.
- Uses a Random Forest Regression model to forecast electricity demand.
- Generates a 24-hour forward demand forecast.
- Compares predicted demand against simulated grid capacity.
- Provides high-risk alerts when demand approaches grid limits.
- Simulates rooftop solar generation to estimate net demand.
- Provides regional demand allocation and localized risk indicators.
  
## Machine Learning
The model uses:
- Temperature
- Humidity
- Hour / Day / Month
- Weekend indicator
- Cooling & Heating indicators
- Previous-hour temperature
- 24-hour demand lag

Prototype performance:
MAE: 143.03 MW
RMSE: 187.26 MW
R²: 0.9807

Note: The prototype uses real historical weather data from Open-Meteo, while electricity-demand values are synthetically generated for development and demonstration.

## Tech Stack
Python · Pandas · NumPy · Scikit-learn · Joblib · Streamlit · Open-Meteo

## Hackathon
Built for the Origin Hackathon — AI-Based Electricity Demand Prediction System.
