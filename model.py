import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Load the CSV dataset
print("Loading dataset...")
df = pd.read_csv("delhi_power_weather_2023.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 2. Creating inputs for the model
df['hour'] = df['timestamp'].dt.hour
df['dayofweek'] = df['timestamp'].dt.dayofweek
df['month'] = df['timestamp'].dt.month
df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

# Cooling and Heating Degree Days
df['cdd'] = np.maximum(0, df['temp_c'] - 22)
df['hdd'] = np.maximum(0, 15 - df['temp_c'])

# past values
df['temp_lag_1h'] = df['temp_c'].shift(1)
df['demand_lag_24h'] = df['actual_demand_mw'].shift(24)

# Drop rows with NaN values created by shift()
df = df.dropna().reset_index(drop=True)

# 3. Define Input Features (X) and Target Output (y)
features = ['hour', 'dayofweek', 'month', 'is_weekend', 'temp_c', 'humidity', 'cdd', 'hdd', 'temp_lag_1h', 'demand_lag_24h']
X = df[features]
y = df['actual_demand_mw']

# 4. Train / Test Split (Time-based: First 80% for training, last 20% for testing)
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# 5. Train Random Forest Model
print("Training Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Evaluate Model Predictions
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("---------------------------------------")
print("✅ Model Trained Successfully!")
print(f"Mean Absolute Error (MAE): {mae:.2f} MW")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f} MW")
print("---------------------------------------")

# 7. Save Predictions to CSV for the Streamlit Dashboard
test_df = df.iloc[split_idx:].copy()
test_df['predicted_demand_mw'] = y_pred
test_df.to_csv("predictions.csv", index=False)
print("Saved predictions to 'predictions.csv'!")