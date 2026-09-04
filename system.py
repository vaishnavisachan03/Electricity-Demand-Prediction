import streamlit as st
import datetime
import math
import random
import joblib
import pandas as pd
import numpy as np

# Load trained model
model = joblib.load("model.pkl")

# Load historical dataset
df = pd.read_csv("delhi_power_weather_2023.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Feature engineering
df["hour"] = df["timestamp"].dt.hour
df["dayofweek"] = df["timestamp"].dt.dayofweek
df["month"] = df["timestamp"].dt.month
df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)

# Cooling and heating features
df["cdd"] = np.maximum(0, df["temp_c"] - 22)
df["hdd"] = np.maximum(0, 15 - df["temp_c"])

# Lag features
df["temp_lag_1h"] = df["temp_c"].shift(1)
df["demand_lag_24h"] = df["actual_demand_mw"].shift(24)

# Page setup
st.set_page_config(
    page_title="Delhi SLDC Demand Forecast",
    layout="wide"
)

GRID_MAX_CAPACITY = 8500.0

st.title("⚡ Delhi AI-Based Short-Term Load Forecasting System")
st.caption("State Load Despatch Centre (SLDC) - Predictive Grid Analytics Platform")

# Sidebar controls
st.sidebar.header("🎛️ Discom Control Center")
st.sidebar.markdown("---")

solar_toggle = st.sidebar.toggle(
    "Enable Net Metering (Rooftop Solar Input)",
    value=False
)

solar_capacity = 0

if solar_toggle:
    solar_capacity = st.sidebar.slider(
        "Peak Solar Penetration (MW)",
        100,
        1500,
        600
    )

temp_offset = st.sidebar.slider(
    "Simulate Heatwave Scenario (Add °C)",
    0.0,
    5.0,
    0.0,
    step=0.5
)

# Generate next 24 hours
now = datetime.datetime.now()

timestamps = [
    now + datetime.timedelta(hours=i)
    for i in range(24)
]

max_future_demand = 0
max_temp = 0
hourly_metrics = []

# Generate AI forecast
for ts in timestamps:

    hour = ts.hour
    dayofweek = ts.weekday()
    month = ts.month
    is_weekend = 1 if dayofweek >= 5 else 0

    # Simulate temperature
    base_temp = 36.5 + temp_offset

    diurnal_variation = 4.5 * math.sin(
        2 * math.pi * (hour - 6) / 24
    )

    temp = (
        base_temp
        + diurnal_variation
        + random.uniform(-0.3, 0.3)
    )

    max_temp = max(max_temp, temp)

    # Simulate humidity
    humidity = random.uniform(35, 70)

    # Calculate cooling and heating features
    cdd = max(0, temp - 22)
    hdd = max(0, 15 - temp)

    # Simulate previous-hour temperature
    temp_lag_1h = temp + random.uniform(-1.0, 1.0)

    # Simulate demand from 24 hours ago
    demand_lag_24h = random.uniform(5000, 7000)

    # Prepare features for the ML model
    features = [[
        hour,
        dayofweek,
        month,
        is_weekend,
        temp,
        humidity,
        cdd,
        hdd,
        temp_lag_1h,
        demand_lag_24h
    ]]

    # Get AI prediction
    gross_demand = model.predict(features)[0]

    # Calculate rooftop solar generation
    solar_generation = 0

    if solar_toggle and 6 <= hour <= 18:
        solar_generation = (
            solar_capacity *
            math.sin(
                math.pi * (hour - 6) / 12
            )
        )

    # Calculate net demand after solar generation
    net_demand = gross_demand - solar_generation

    max_future_demand = max(
        max_future_demand,
        net_demand
    )

    hourly_metrics.append({
        "time": ts.strftime("%H:%M"),
        "temp": round(temp, 1),
        "demand": round(net_demand, 1)
    })

# Display grid alerts
if max_future_demand > GRID_MAX_CAPACITY:

    st.error(
        f"🚨 CRITICAL ALERT: Forecasted peak "
        f"({max_future_demand:.1f} MW) EXCEEDS Grid Limits "
        f"({GRID_MAX_CAPACITY} MW)! Initiate load-shedding schedules."
    )

elif max_future_demand >= GRID_MAX_CAPACITY * 0.9:

    st.warning(
        f"⚠️ HIGH RISK: Peak demand will touch "
        f"{max_future_demand:.1f} MW. "
        f"Grid reserves are running critically below 10%."
    )

else:

    st.success(
        "✅ GRID STABLE: Supply metrics healthy. "
        "Demand safely within reserve boundaries."
    )

# KPI summary
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Peak Forecasted Load",
    f"{max_future_demand:.1f} MW"
)

col2.metric(
    "Total Grid Capacity",
    f"{GRID_MAX_CAPACITY} MW"
)

col3.metric(
    "Projected Peak Temp",
    f"{max_temp:.1f} °C"
)

col4.metric(
    "Solar Offset",
    f"{solar_capacity if solar_toggle else 0} MW Max"
)

# Hourly forecast display
st.subheader("📊 24-Hour Forward Forecast Matrix")

st.markdown(
    "AI-generated hourly electricity demand forecast "
    "based on weather and temporal features:"
)

for item in hourly_metrics[::2]:

    load_ratio = item["demand"] / GRID_MAX_CAPACITY

    percentage_fill = min(
        100,
        int(load_ratio * 100)
    )

    # Determine risk indicator
    color_indicator = "🟢"

    if percentage_fill > 92:
        color_indicator = "🔴"

    elif percentage_fill > 85:
        color_indicator = "🟡"

    col_t, col_b = st.columns([1, 6])

    with col_t:
        st.markdown(
            f"**{item['time']}** ({item['temp']}°C)"
        )

    with col_b:
        st.progress(
            min(load_ratio, 1.0)
        )

        st.caption(
            f"{color_indicator} Forecasted Load: "
            f"**{item['demand']} MW** "
            f"({percentage_fill}% capacity utilization)"
        )

# Regional feeder analysis
st.markdown("---")

st.subheader(
    "🗺️ Regional Feeder Allocations & Localized Risks"
)

zones = {
    "BRPL (South & West Delhi)": 0.42,
    "BYPL (Central & East Delhi)": 0.28,
    "TPDDL (North Delhi)": 0.22,
    "NDMC Area": 0.08
}

zone_cols = st.columns(4)

for idx, (name, percentage) in enumerate(zones.items()):

    with zone_cols[idx]:

        regional_peak = (
            max_future_demand * percentage
        )

        regional_limit = (
            GRID_MAX_CAPACITY * percentage
        )

        risk_pct = min(
            100.0,
            (regional_peak / regional_limit) * 100
        )

        st.markdown(f"#### {name}")

        st.metric(
            "Peak Demand",
            f"{regional_peak:.1f} MW"
        )

        st.progress(
            risk_pct / 100
        )

        # Determine regional status
        if risk_pct > 95:
            status = f"🔴 Overload ({risk_pct:.1f}%)"

        elif risk_pct > 88:
            status = f"🟡 High Stress ({risk_pct:.1f}%)"

        else:
            status = f"🟢 Normal ({risk_pct:.1f}%)"

        st.caption(
            f"Status: {status}"
        )
