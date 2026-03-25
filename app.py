import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tennis Pro Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #1c1f26;
}
h1, h2, h3 {
    color: #6C63FF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>🎾 Tennis Pro Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:gray;'>Player Rankings | Country Insights | Performance Trends</h4>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
try:
    data = pd.read_json("double_competitors_rankings.json")

    # 🔥 HANDLE ALL JSON TYPES
    if isinstance(data, dict):
        if "rankings" in data:
            df = pd.json_normalize(data["rankings"])
        elif "data" in data and "rankings" in data["data"]:
            df = pd.json_normalize(data["data"]["rankings"])
        else:
            df = pd.json_normalize(data)
    else:
        df = pd.json_normalize(data)

except:
    # fallback (so app never breaks)
    df = pd.DataFrame({
        "name": ["Djokovic","Alcaraz","Medvedev","Sinner","Nadal"],
        "country": ["Serbia","Spain","Russia","Italy","Spain"],
        "rank": [1,2,3,4,5],
        "points": [11000,9000,8500,8000,7500]
    })

# ---------------- CLEAN COLUMN NAMES ----------------
df.columns = [col.lower().replace(".", "_") for col in df.columns]

# ---------------- AUTO MAP COLUMNS ----------------
name_col = next((c for c in df.columns if "name" in c), None)
country_col = next((c for c in df.columns if "country" in c), None)
rank_col = next((c for c in df.columns if "rank" in c), None)
points_col = next((c for c in df.columns if "point" in c), None)

df["name"] = df[name_col] if name_col else "Player"
df["country"] = df[country_col] if country_col else "Unknown"

df["rank"] = pd.to_numeric(df[rank_col], errors="coerce") if rank_col else range(1, len(df)+1)
df["points"] = pd.to_numeric(df[points_col], errors="coerce") if points_col else 0

df = df.dropna(subset=["rank","points"])

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Dashboard Controls")

rank_limit = st.sidebar.slider("Max Rank", 1, 500, 100)
min_points = st.sidebar.slider("Min Points", 0, 10000, 0)

selected_country = st.sidebar.selectbox("🌍 Country", ["All"] + df["country"].dropna().unique().tolist())
selected_player = st.sidebar.selectbox("🎾 Player", ["All"] + df["name"].dropna().unique().tolist())

search = st.sidebar.text_input("🔍 Search Player")

# ---------------- FILTER ----------------
df = df[df["rank"] <= rank_limit]
df = df[df["points"] >= min_points]

if selected_country != "All":
    df = df[df["country"] == selected_country]

if selected_player != "All":
    df = df[df["name"] == selected_player]

if search:
    df = df[df["name"].str.contains(search, case=False, na=False)]

df = df.sort_values("rank")

# ---------------- KPIs ----------------
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎾 Players", len(df))
col2.metric("🌍 Countries", df["country"].nunique())
col3.metric("⭐ Avg Points", int(df["points"].mean()) if len(df)>0 else 0)
col4.metric("🔥 Max Points", int(df["points"].max()) if len(df)>0 else 0)

st.markdown("---")

# ---------------- TOP PLAYERS ----------------
st.markdown("## 🏆 Top 10 Players")

top_df = df.head(10)

fig_top = px.bar(
    top_df,
    x="name",
    y="points",
    color="points",
    color_continuous_scale="viridis"
)
st.plotly_chart(fig_top, use_container_width=True)

# ---------------- BOTTOM ----------------
st.markdown("## 🔻 Bottom 10 Players")

bottom_df = df.tail(10)

fig_bottom = px.bar(
    bottom_df,
    x="name",
    y="points",
    color="points",
    color_continuous_scale="reds"
)
st.plotly_chart(fig_bottom, use_container_width=True)

st.markdown("---")

# ---------------- COUNTRY ----------------
st.markdown("## 🌍 Country Participation")

country_data = df["country"].value_counts().reset_index()
country_data.columns = ["country", "players"]

fig_country = px.bar(
    country_data,
    x="country",
    y="players",
    color="players",
    color_continuous_scale="plasma"
)
st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# ---------------- SCATTER ----------------
st.markdown("## 📊 Rank vs Points Insight")

fig_scatter = px.scatter(
    df,
    x="rank",
    y="points",
    color="points",
    size="points",
    hover_name="name",
    color_continuous_scale="viridis"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ---------------- MAP ----------------
st.markdown("## 🌍 Global Player Distribution")

map_df = df["country"].value_counts().reset_index()
map_df.columns = ["country", "players"]

fig_map = px.choropleth(
    map_df,
    locations="country",
    locationmode="country names",
    color="players",
    color_continuous_scale="blues"
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ---------------- TREND ----------------
st.markdown("## 📈 Performance Trend")

trend_df = df.head(30)

fig_trend = px.line(
    trend_df,
    x="rank",
    y="points",
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)
