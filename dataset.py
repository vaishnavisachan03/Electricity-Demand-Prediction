import pandas as pd
import numpy as np
import requests

print("Fetching weather data from Open-Meteo")

np.random.seed(42)

#fetch data
url = (
    "https://archive-api.open-meteo.com/v1/archive?"
    "latitude=28.6139&longitude=77.2090&"
    "start_date=2023-01-01&end_date=2023-12-31&"
    "hourly=temperature_2m,relative_humidity_2m,direct_normal_irradiance"
)

response = requests.get(url).json()

df = pd.DataFrame({
    'timestamp': pd.to_datetime(response['hourly']['time']),
    'temp_c': response['hourly']['temperature_2m'],
    'humidity': response['hourly']['relative_humidity_2m'],
    'solar_irradiance': response['hourly']['direct_normal_irradiance']
})

# 2. Generate Calibrated Electricity Demand Load (in megawatt)
base_load = 5000
summer_cooling = np.maximum(0, df['temp_c'] - 22) ** 1.85 * 180
winter_heating = np.maximum(0, 15 - df['temp_c']) ** 1.4 * 60
time_of_day = np.sin((df['timestamp'].dt.hour - 6) * np.pi / 12) * 800
noise = np.random.normal(0, 150, len(df))

df['actual_demand_mw'] = np.clip(base_load + summer_cooling + winter_heating + time_of_day + noise, 2000, 7800)


# 3. Save to CSV
df.to_csv("delhi_power_weather_2023.csv", index=False)
print(" Dataset successfully generated with 'actual_demand_mw' column!")