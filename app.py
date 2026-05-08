import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lake Chad Basin — Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1c1f2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #e05c5c; }
    .metric-label { font-size: 0.85rem; color: #aaa; margin-top: 4px; }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #c9d1d9;
        border-left: 3px solid #e05c5c;
        padding-left: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/ucdp_lake_chad_clean.csv", parse_dates=["date"])
    return df

df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.image("https://flagcdn.com/w40/ng.png", width=30)
st.sidebar.title("🛡️ Lake Chad Basin")
st.sidebar.markdown("**Security Dashboard**")
st.sidebar.markdown("---")

# Country filter
countries = ["All"] + sorted(df["country"].unique().tolist())
selected_country = st.sidebar.selectbox("🌍 Country", countries)

# Year filter
years = sorted(df["year"].dropna().unique().tolist())
selected_years = st.sidebar.slider(
    "📅 Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# Violence type filter
violence_types = ["All"] + sorted(df["violence_type"].unique().tolist())
selected_violence = st.sidebar.selectbox("⚔️ Violence Type", violence_types)

# Map style
map_style = st.sidebar.radio("🗺️ Map View", ["Heatmap", "Clustered Markers"])

st.sidebar.markdown("---")
st.sidebar.markdown("📊 Data: [UCDP GED v25.1](https://ucdp.uu.se/downloads)")
st.sidebar.markdown("🗓️ Coverage: 2015–2024")

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
filtered = df.copy()

if selected_country != "All":
    filtered = filtered[filtered["country"] == selected_country]

filtered = filtered[
    (filtered["year"] >= selected_years[0]) &
    (filtered["year"] <= selected_years[1])
]

if selected_violence != "All":
    filtered = filtered[filtered["violence_type"] == selected_violence]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🛡️ Lake Chad Basin Security Dashboard")
st.markdown(f"Showing **{len(filtered):,}** conflict events · {selected_years[0]}–{selected_years[1]}")
st.markdown("---")

# ── METRICS ROW ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{len(filtered):,}</div>
        <div class='metric-label'>Total Events</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{filtered['deaths_total'].sum():,}</div>
        <div class='metric-label'>Total Deaths</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{filtered['deaths_civilians'].sum():,}</div>
        <div class='metric-label'>Civilian Deaths</div>
    </div>""", unsafe_allow_html=True)

with c4:
    severe = len(filtered[filtered["severity"] == "Severe (50+)"])
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{severe:,}</div>
        <div class='metric-label'>Severe Incidents</div>
    </div>""", unsafe_allow_html=True)

with c5:
    top_conflict = filtered["conflict"].value_counts().index[0] if len(filtered) > 0 else "N/A"
    short = top_conflict[:20] + "..." if len(top_conflict) > 20 else top_conflict
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value' style='font-size:1rem'>{short}</div>
        <div class='metric-label'>Top Conflict</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAP ───────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>📍 Conflict Map</div>", unsafe_allow_html=True)

map_data = filtered.dropna(subset=["latitude", "longitude"])

m = folium.Map(
    location=[12.0, 13.5],
    zoom_start=6,
    tiles="CartoDB dark_matter"
)

if map_style == "Heatmap":
    heat_data = map_data[["latitude", "longitude", "deaths_total"]].values.tolist()
    HeatMap(heat_data, radius=10, blur=15, max_zoom=8).add_to(m)

else:
    cluster = MarkerCluster().add_to(m)
    color_map = {
        "State-based conflict":  "red",
        "Non-state conflict":    "orange",
        "One-sided (civilians)": "darkred",
    }
    for _, row in map_data.iterrows():
        color = color_map.get(row["violence_type"], "gray")
        popup_text = f"""
            <b>{row['conflict']}</b><br>
            📅 {str(row['date'])[:10]}<br>
            📍 {row.get('location_name', row['state_province'])}<br>
            ⚔️ {row['violence_type']}<br>
            💀 Deaths: {row['deaths_total']}
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(cluster)

st_folium(m, width="100%", height=500)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHARTS ROW ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='section-title'>📈 Events Over Time</div>", unsafe_allow_html=True)
    timeline = filtered.groupby("year_month").agg(
        events=("id", "count"),
        deaths=("deaths_total", "sum")
    ).reset_index()
    timeline["year_month"] = timeline["year_month"].astype(str)

    fig1 = px.bar(
        timeline, x="year_month", y="events",
        color="deaths", color_continuous_scale="Reds",
        labels={"year_month": "Month", "events": "Events", "deaths": "Deaths"},
        template="plotly_dark"
    )
    fig1.update_layout(margin=dict(t=10, b=40), height=320, showlegend=False)
    fig1.update_xaxes(tickangle=45, nticks=20)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("<div class='section-title'>⚔️ Violence Type Breakdown</div>", unsafe_allow_html=True)
    vtype = filtered["violence_type"].value_counts().reset_index()
    vtype.columns = ["type", "count"]

    fig2 = px.pie(
        vtype, names="type", values="count",
        color_discrete_sequence=["#e05c5c", "#f0a500", "#5c7ae0"],
        template="plotly_dark", hole=0.4
    )
    fig2.update_layout(margin=dict(t=10), height=320)
    st.plotly_chart(fig2, use_container_width=True)

# ── SECOND CHARTS ROW ─────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='section-title'>🗺️ Most Affected States/Provinces</div>", unsafe_allow_html=True)
    top_states = filtered.groupby("state_province").agg(
        events=("id", "count"),
        deaths=("deaths_total", "sum")
    ).sort_values("events", ascending=False).head(12).reset_index()

    fig3 = px.bar(
        top_states, x="events", y="state_province",
        orientation="h", color="deaths",
        color_continuous_scale="Reds",
        labels={"state_province": "", "events": "Events", "deaths": "Deaths"},
        template="plotly_dark"
    )
    fig3.update_layout(margin=dict(t=10, b=10), height=350, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("<div class='section-title'>💀 Top 10 Deadliest Conflicts</div>", unsafe_allow_html=True)
    top_conflicts = filtered.groupby("conflict").agg(
        events=("id", "count"),
        deaths=("deaths_total", "sum")
    ).sort_values("deaths", ascending=False).head(10).reset_index()

    fig4 = px.bar(
        top_conflicts, x="deaths", y="conflict",
        orientation="h", color="events",
        color_continuous_scale="Oranges",
        labels={"conflict": "", "deaths": "Deaths", "events": "Events"},
        template="plotly_dark"
    )
    fig4.update_layout(margin=dict(t=10, b=10), height=350, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig4, use_container_width=True)

# ── DATA TABLE ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-title'>📋 Raw Event Data</div>", unsafe_allow_html=True)

show_cols = ["date", "country", "state_province", "conflict",
             "violence_type", "deaths_total", "severity", "headline"]
available = [c for c in show_cols if c in filtered.columns]

st.dataframe(
    filtered[available].sort_values("date", ascending=False).head(500),
    use_container_width=True,
    height=300
)

st.caption(f"Showing top 500 most recent events out of {len(filtered):,} total")
