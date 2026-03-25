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
data = pd.read_json("double_competitors_rankings.json")

# 🔥 FIX JSON STRUCTURE
df = pd.json_normalize(data["rankings"])

# Extract correct columns
# 🔥 AUTO DETECT NAME COLUMN
name_col = [col for col in df.columns if "name" in col.lower()]
country_col = [col for col in df.columns if "country" in col.lower()]

if name_col:
    df["name"] = df[name_col[0]]
else:
    df["name"] = "Unknown"

if country_col:
    df["country"] = df[country_col[0]]
else:
    df["country"] = "Unknown"
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
# 🔥 AUTO DETECT RANK
rank_col = [col for col in df.columns if "rank" in col.lower()]

if rank_col:
    df["rank"] = df[rank_col[0]]
else:
    df["rank"] = range(1, len(df)+1)

# 🔥 AUTO DETECT POINTS
points_col = [col for col in df.columns if "point" in col.lower()]

if points_col:
    df["points"] = df[points_col[0]]
else:
    df["points"] = 0

# APPLY FILTERS
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

# ---------------- BOTTOM PLAYERS ----------------
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

# ---------------- BOX ----------------
fig_box = px.box(
    df,
    x="country",
    y="rank",
    color="country"
)

st.plotly_chart(fig_box, use_container_width=True)

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
