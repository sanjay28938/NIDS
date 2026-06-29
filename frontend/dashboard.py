import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="AI NIDS SOC Dashboard",
    layout="wide"
)

# ===============================
# HEADER
# ===============================
st.title("🛡  Cyber Security Dashboard")

st.subheader("📍 Monitored Location")
st.success("Bangalore, Karnataka, India")

# ===============================
# PATHS
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "alerts.log"

# ===============================
# AUTO REFRESH
# ===============================
st_autorefresh(interval=3000, key="refresh")

# ===============================
# LOAD LOGS
# ===============================
try:

    df = pd.read_csv(
    LOG_FILE,
    sep="|",
    header=None,
    engine="python",
    encoding="latin1",
    on_bad_lines="skip"
)

    # Remove spaces
    df = df.apply(
        lambda col: col.map(
            lambda x: x.strip() if isinstance(x, str) else x
        )
    )

    # Keep only rows with enough columns
    df = df[df.notnull().sum(axis=1) >= 10]

    # Keep first 10 columns only
    df = df.iloc[:, :10]

    # Rename columns
    df.columns = [
        "time",
        "event",
        "attack",
        "severity",
        "ip",
        "country",
        "lat",
        "lon",
        "asn",
        "organization"
    ]

    # Debug
    st.write("Logs Loaded:", len(df))

except Exception as e:

    st.error(f"Error Loading Logs: {e}")
    st.stop()

# ===============================
# CLEAN DATA
# ===============================
df = df.fillna({
    "attack": "Normal",
    "severity": "LOW",
    "country": "Unknown",
    "lat": 0,
    "lon": 0,
    "asn": "Unknown",
    "organization": "Unknown"
})

df["event"] = df["event"].astype(str).str.strip()
df["attack"] = df["attack"].astype(str).str.strip()
df["severity"] = df["severity"].astype(str).str.strip()
df["country"] = df["country"].astype(str).str.strip()
df["asn"] = df["asn"].astype(str).str.strip()
df["organization"] = df["organization"].astype(str).str.strip()

df["lat"] = pd.to_numeric(df["lat"], errors="coerce").fillna(0)
df["lon"] = pd.to_numeric(df["lon"], errors="coerce").fillna(0)

df["time"] = pd.to_datetime(df["time"], errors="coerce")

# Keep latest logs only
df = df.tail(1000)

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header(" Filters")

event_filter = st.sidebar.multiselect(
    "Traffic Type",
    ["ATTACK", "NORMAL"],
    default=["ATTACK", "NORMAL"]
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    default=["LOW", "MEDIUM", "HIGH", "CRITICAL"]
)

filtered_df = df[
    df["event"].isin(event_filter) &
    df["severity"].isin(severity_filter)
]

# ===============================
# METRICS
# ===============================
attack_count = filtered_df[
    filtered_df["event"] == "ATTACK"
].shape[0]

normal_count = filtered_df[
    filtered_df["event"] == "NORMAL"
].shape[0]

critical_count = filtered_df[
    filtered_df["severity"] == "CRITICAL"
].shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("🚨 Total Alerts", len(filtered_df))
col2.metric("✅ Normal Traffic", normal_count)
col3.metric("🌐 Unique Attackers", filtered_df["ip"].nunique())
col4.metric("☠︎︎ Critical Threats", critical_count)

# ===============================
# THREAT LEVEL
# ===============================
st.subheader("🔥 Live Threat Level")

if len(filtered_df) == 0:
    risk_score = 0
else:
    risk_score = int((attack_count / len(filtered_df)) * 100)

st.progress(risk_score)

if risk_score > 75:
    st.error("🚨 CRITICAL RISK")
elif risk_score > 50:
    st.warning("⚠ HIGH RISK")
elif risk_score > 25:
    st.info("ℹ MEDIUM RISK")
else:
    st.success("🔋 LOW RISK")

# ===============================
# ATTACK DISTRIBUTION
# ===============================
st.subheader("📊 Attack Distribution")

type_df = (
    filtered_df["attack"]
    .value_counts()
    .reset_index()
)

type_df.columns = ["Attack", "Count"]

fig1 = px.bar(
    type_df,
    x="Attack",
    y="Count",
    color="Attack",
    template="plotly_dark"
)

st.plotly_chart(fig1, use_container_width=True)

# ===============================
# ATTACK TIMELINE
# ===============================
st.subheader("⏱ Attack Timeline")

timeline = (
    filtered_df
    .set_index("time")
    .resample("1min")
    .size()
    .reset_index(name="Attacks")
)

fig2 = px.area(
    timeline,
    x="time",
    y="Attacks",
    template="plotly_dark"
)

st.plotly_chart(fig2, use_container_width=True)

# ===============================
# LIVE GLOBAL ATTACK MAP
# ===============================
st.subheader("🌍 Live Global Threat Sources")

# ===============================
# FILTER ATTACKS ONLY
# ===============================
attack_df = filtered_df[
    filtered_df["event"] == "ATTACK"
].copy()

# ===============================
# CLEAN COORDINATES
# ===============================
attack_df["lat"] = pd.to_numeric(
    attack_df["lat"],
    errors="coerce"
)

attack_df["lon"] = pd.to_numeric(
    attack_df["lon"],
    errors="coerce"
)

# ===============================
# REMOVE INVALID LOCATIONS
# ===============================
attack_df = attack_df[
    (attack_df["lat"] != 0) &
    (attack_df["lon"] != 0)
]

# ===============================
# ROTATING ATTACK BATCHES
# ===============================

if "map_index" not in st.session_state:
    st.session_state.map_index = 0

batch_size = 10

total_logs = len(attack_df)

start = st.session_state.map_index
end = start + batch_size

# Current 10 logs
attack_df = attack_df.iloc[start:end]

# Move to next logs
if end < total_logs:

    st.session_state.map_index += batch_size

else:

    st.session_state.map_index = 0

# ===============================
# TARGET LOCATION (BANGALORE)
# ===============================
TARGET_LAT = 12.9716
TARGET_LON = 77.5946

# ===============================
# CREATE MAP
# ===============================
fig3 = go.Figure()

# ===============================
# PLOT ATTACKS
# ===============================
for _, row in attack_df.iterrows():

    # ===============================
    # SEVERITY COLOR
    # ===============================
    marker_color = {

        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "yellow",
        "LOW": "green"

    }.get(row["severity"], "white")

    # ===============================
    # ATTACK SOURCE MARKER
    # ===============================
    fig3.add_trace(go.Scattergeo(

        lat=[row["lat"]],
        lon=[row["lon"]],

        mode="markers+text",

        text=[row["country"]],
        textposition="top center",

        marker=dict(
            size=10,
            color=marker_color,
            opacity=0.8
        ),

        hovertext=(

            f"🌍 Country: {row['country']}<br>"
            f"📡 IP: {row['ip']}<br>"
            f"⚠ Attack: {row['attack']}<br>"
            f"🔥 Severity: {row['severity']}<br>"
            f"🏢 ASN: {row['asn']}<br>"
            f"🏛 Organization: {row['organization']}"

        ),

        hoverinfo="text",

        showlegend=False
    ))

    # ===============================
    # CONNECTION LINE TO TARGET
    # ===============================
    fig3.add_trace(go.Scattergeo(

        lat=[row["lat"], TARGET_LAT],
        lon=[row["lon"], TARGET_LON],

        mode="lines",

        line=dict(
            width=1,
            color=marker_color
        ),

        opacity=0.5,

        showlegend=False
    ))

# ===============================
# TARGET MARKER
# ===============================
fig3.add_trace(go.Scattergeo(

    lat=[TARGET_LAT],
    lon=[TARGET_LON],

    mode="markers+text",

    text=["Bangalore"],

    textposition="bottom center",

    marker=dict(
        size=14,
        color="red"
    ),

    name="Target"
))

# ===============================
# MAP LAYOUT
# ===============================
fig3.update_layout(

    template="plotly_dark",

    geo=dict(

        projection_type="natural earth",

        showland=True,
        landcolor="rgb(20,20,20)",

        showcountries=True,

        showcoastlines=True,
        coastlinecolor="gray",

        showocean=True,
        oceancolor="rgb(10,10,30)"
    ),

    height=750,

    margin=dict(
        l=0,
        r=0,
        t=40,
        b=0
    )
)

# ===============================
# SHOW MAP
# ===============================
st.plotly_chart(
    fig3,
    use_container_width=True
)
# ===============================
# TOP ATTACKERS
# ===============================
st.subheader("💀 Top Attacker IPs")

top_ips = (
    filtered_df["ip"]
    .value_counts()
    .head(10)
    .reset_index()
)

top_ips.columns = ["IP", "Attacks"]

fig4 = px.bar(
    top_ips,
    x="IP",
    y="Attacks",
    color="Attacks",
    template="plotly_dark"
)

st.plotly_chart(fig4, use_container_width=True)

# ===============================
# TOP COUNTRIES
# ===============================
st.subheader("🌍 Top Attacking Countries")

country_df = (
    filtered_df["country"]
    .value_counts()
    .head(10)
    .reset_index()
)

country_df.columns = ["Country", "Attacks"]

fig5 = px.bar(
    country_df,
    x="Attacks",
    y="Country",
    orientation="h",
    color="Attacks",
    template="plotly_dark"
)

st.plotly_chart(fig5, use_container_width=True)

# ===============================
# ASN THREAT INTELLIGENCE
# ===============================
st.subheader("🌐 ASN Threat Intelligence")

asn_df = (
    filtered_df["organization"]
    .value_counts()
    .head(10)
    .reset_index()
)

asn_df.columns = ["Organization", "Threats"]

fig6 = px.bar(
    asn_df,
    x="Threats",
    y="Organization",
    orientation="h",
    color="Threats",
    template="plotly_dark"
)

st.plotly_chart(fig6, use_container_width=True)

# ===============================
# AI THREAT INTELLIGENCE
# ===============================
st.subheader("🧠 AI Threat Intelligence")

if not filtered_df.empty:

    top_attack = filtered_df["attack"].value_counts().idxmax()
    top_country = filtered_df["country"].value_counts().idxmax()

    col1, col2 = st.columns(2)

    col1.metric("🔥 Top Threat", top_attack)
    col2.metric("🌍 Top Attack Country", top_country)

    st.progress(risk_score)

    if risk_score > 75:
        st.error("🚨 Critical Threat Level")
    elif risk_score > 50:
        st.warning("⚠ High Threat Level")
    elif risk_score > 25:
        st.info("ℹ Moderate Threat Level")
    else:
        st.success("✅ System Stable")

# ===============================
# LIVE ALERTS
# ===============================
st.subheader("🚨 Live Alerts")

for _, row in filtered_df.tail(15).iterrows():

    msg = (
        f"{row['attack']} | "
        f"{row['country']} | "
        f"{row['asn']} | "
        f"{row['organization']}"
    )

    if row["severity"] == "CRITICAL":
        st.error(msg)

    elif row["severity"] == "HIGH":
        st.warning(msg)

    elif row["severity"] == "MEDIUM":
        st.info(msg)

    else:
        st.success(msg)

# ===============================
# GLOBAL ATTACK MAP
# ===============================
st.subheader("🌍 Global Attack Distribution")

country_map = (
    filtered_df
    .groupby("country")
    .size()
    .reset_index(name="attacks")
)

fig7 = px.choropleth(
    country_map,
    locations="country",
    locationmode="country names",
    color="attacks",
    color_continuous_scale="Turbo",
    template="plotly_dark"
)

fig7.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type="natural earth"
    )
)

st.plotly_chart(fig7, use_container_width=True)

# ===============================
# ACTIVITY FEED
# ===============================
st.subheader("💻 Activity Feed")

st.dataframe(
    filtered_df.tail(20),
    use_container_width=True,
    height=400
)

# ===============================
# SIDEBAR INFO
# ===============================
st.sidebar.success("🟢 System Status: ACTIVE")

st.sidebar.metric(
    "🌍 Countries",
    filtered_df["country"].nunique()
)

st.sidebar.metric(
    "⚔ Attack Types",
    filtered_df["attack"].nunique()
)

st.sidebar.write(
    f"Last Updated: {pd.Timestamp.now()}"
)

# ===============================
# DOWNLOAD LOGS
# ===============================
st.sidebar.download_button(
    label="📥 Download Logs",
    data=filtered_df.to_csv(index=False),
    file_name="alerts.csv",
    mime="text/csv"
)