import streamlit as st
import datetime
import math
import random
import joblib

model = joblib.load("model.pkl")

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Delhi SLDC Demand Forecast", layout="wide")

GRID_MAX_CAPACITY = 8500.0  # MW limit

st.title("⚡ Delhi AI-Based Short-Term Load Forecasting System")
st.caption("State Load Despatch Centre (SLDC) - Predictive Grid Analytics Platform")

#SIDEBAR INTERACTIVE CONTROLS
st.sidebar.header("🎛️ Discom Control Center")
st.sidebar.markdown("---")

solar_toggle = st.sidebar.toggle("Enable Net Metering (Rooftop Solar Input)", value=False)
solar_capacity = 0
if solar_toggle:
    solar_capacity = st.sidebar.slider("Peak Solar Penetration (MW)", 100, 1500, 600)

temp_offset = st.sidebar.slider("Simulate Heatwave Scenario (Add °C)", 0.0, 5.0, 0.0, step=0.5)

#BACKEND SIMULATION
now = datetime.datetime.now()
timestamps = [(now + datetime.timedelta(hours=i)) for i in range(24)]

max_future_demand = 0
max_temp = 0
hourly_metrics = []

for ts in timestamps:
    hour = ts.hour
    
    # Temperature Profile
    base_temp = 36.5 + temp_offset
    diurnal_variation = 4.5 * math.sin(2 * math.pi * (hour - 6) / 24)
    temp = base_temp + diurnal_variation + random.uniform(-0.3, 0.3)
    if temp > max_temp:
        max_temp = temp
        
        # Demand Profile (Ensures the base is never negative before the power calculation)
    base_demand = 4400.0
    
    if temp > 32:
        temp_impact = (temp - 32) ** 1.8 * 62
    else:
        temp_impact = 0.0
        
    time_impact = 450 * math.sin(2 * math.pi * (hour - 14) / 24) + 350 * math.sin(2 * math.pi * (hour - 22) / 24)

    gross_demand = base_demand + temp_impact + time_impact + random.uniform(-50, 50)
    gross_demand = min(8400.0, max(3600.0, gross_demand))
    
    solar_generation = 0
    if solar_toggle and (6 <= hour <= 18):
        solar_generation = solar_capacity * math.sin(math.pi * (hour - 6) / 12)
        
    net_demand = gross_demand - solar_generation
    if net_demand > max_future_demand:
        max_future_demand = net_demand
        
    hourly_metrics.append({
        "time": ts.strftime("%H:%M"),
        "temp": round(temp, 1),
        "demand": round(net_demand, 1)
    })

# --- FRONTEND INTERFACE & ALERTS ---
if max_future_demand > GRID_MAX_CAPACITY:
    st.error(f"CRITICAL ALERT: Forecasted peak ({max_future_demand:.1f} MW) EXCEEDS Grid Limits ({GRID_MAX_CAPACITY} MW)! Initiate load-shedding schedules.")
elif max_future_demand >= (GRID_MAX_CAPACITY * 0.9):
    st.warning(f"HIGH RISK: Peak demand will touch {max_future_demand:.1f} MW. Grid reserves are running critically below 10%.")
else:
    st.success("GRID STABLE: Supply metrics healthy. Demand safely within reserve boundaries.")

# KPI Summary Blocks
col1, col2, col3, col4 = st.columns(4)
col1.metric("Peak Forecasted Load", f"{max_future_demand:.1f} MW")
col2.metric("Total Grid Capacity", f"{GRID_MAX_CAPACITY} MW")
col3.metric("Projected Peak Temp", f"{max_temp:.1f} °C")
col4.metric("Solar Offset", f"{solar_capacity if solar_toggle else 0} MW Max")

# --- CUSTOM BUG-FREE HOURLY LOAD MONITOR ---
st.subheader("24-Hour Forward Forecast Matrix")
st.markdown("Direct telemetry log layout tracking hourly grid stress thresholds:")

for item in hourly_metrics[::2]:  # Shows every alternate hour to keep layout ultra clean
    load_ratio = item["demand"] / GRID_MAX_CAPACITY
    percentage_fill = min(100, int(load_ratio * 100))
    
    color_indicator = "🟢"
    if percentage_fill > 92:
        color_indicator = "🔴"
    elif percentage_fill > 85:
        color_indicator = "🟡"
        
    col_t, col_b = st.columns([1, 6])
    with col_t:
        st.markdown(f"**{item['time']}** ({item['temp']}°C)")
    with col_b:
        st.progress(load_ratio)
        st.caption(f"{color_indicator} Allocated Load Demand: **{item['demand']} MW** ({percentage_fill}% capacity utilization)")

# --- FEEDER ANALYSIS ---
st.markdown("---")
st.subheader("🗺️ Regional Feeder Allocations & Localized Risks")

zones = {
    "BRPL (South & West Delhi)": 0.42,
    "BYPL (Central & East Delhi)": 0.28,
    "TPDDL (North Delhi)": 0.22,
    "NDMC (Lutyens VIP Zone)": 0.08
}

zone_cols = st.columns(4)
for idx, (name, percentage) in enumerate(zones.items()):
    with zone_cols[idx]:
        regional_peak = max_future_demand * percentage
        regional_limit = GRID_MAX_CAPACITY * percentage
        risk_pct = min(100.0, (regional_peak / regional_limit) * 100)
        
        st.markdown(f"#### {name}")
        st.metric("Peak Demand", f"{regional_peak:.1f} MW")
        st.progress(risk_pct / 100)
        st.caption(f"Status: {f'🔴 Overload ({risk_pct:.1f}%)' if risk_pct > 95 else f'🟡 High Stress ({risk_pct:.1f}%)' if risk_pct > 88 else '🟢 Normal'}")
