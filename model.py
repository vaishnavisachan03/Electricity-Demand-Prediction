import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# 1. Load Dataset
df = pd.read_csv("delhi_power_weather_2023.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 2. Feature Engineering
df['hour'] = df['timestamp'].dt.hour
df['dayofweek'] = df['timestamp'].dt.dayofweek
df['month'] = df['timestamp'].dt.month
df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

df['cdd'] = np.maximum(0, df['temp_c'] - 22)
df['hdd'] = np.maximum(0, 15 - df['temp_c'])

df['temp_lag_1h'] = df['temp_c'].shift(1)
df['demand_lag_24h'] = df['actual_demand_mw'].shift(24)

df = df.dropna().reset_index(drop=True)

# 3. Features & Target
features = ['hour', 'dayofweek', 'month', 'is_weekend', 'temp_c', 'humidity', 'cdd', 'hdd', 'temp_lag_1h', 'demand_lag_24h']
X = df[features]
y = df['actual_demand_mw']

# 4. Train / Test Split
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# 5. Train Model
print("Training Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Save Trained Model Object for Live Inference
joblib.dump(model, "model.pkl")
print("Saved trained model as 'model.pkl'")

# 7. Evaluate Performance
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f} MW | RMSE: {rmse:.2f} MW | R² Score: {r2:.4f}")

# 8. Export Feature Importance CSV for Dashboard Charts
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values(by='Importance', ascending=False)

importance_df.to_csv("feature_importances.csv", index=False)
print("Saved feature importances to 'feature_importances.csv'")

# 9. Save Predictions to CSV
test_df = df.iloc[split_idx:].copy()
test_df['predicted_demand_mw'] = y_pred
test_df.to_csv("predictions.csv", index=False)
print("Saved test set prediction")
