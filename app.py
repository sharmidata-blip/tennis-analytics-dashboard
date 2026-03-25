import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tennis Pro Dashboard", layout="wide")

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;color:#6C63FF;'>🎾 Tennis Pro Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:gray;'>Player Rankings | Country Insights | Performance Trends</h4>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_json("double_competitors_rankings.json")

# Normalize JSON
df = pd.json_normalize(df)

# 🔥 AUTO FIX COLUMN NAMES (IMPORTANT)
df.columns = [col.lower().replace(".", "_") for col in df.columns]

# ---------------- SAFE COLUMN DETECTION ----------------

# Detect name column
name_col = None
for col in df.columns:
    if "name" in col:
        name_col = col
        break

# Detect country column
country_col = None
for col in df.columns:
    if "country" in col:
        country_col = col
        break

# Detect rank and points
rank_col = "rank" if "rank" in df.columns else None
points_col = "points" if "points" in df.columns else None

# Rename to standard names
df = df.rename(columns={
    name_col: "name",
    country_col: "country",
    rank_col: "rank",
    points_col: "points"
})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Dashboard Controls")

rank_limit = st.sidebar.slider("Max Rank", 1, 500, 100)
min_points = st.sidebar.slider("Min Points", 0, 10000, 0)

# ---------------- FILTERS ----------------

country_df = df[['country']].drop_duplicates()
selected_country = st.sidebar.selectbox("🌍 Country", ["All"] + country_df["country"].dropna().tolist())

player_df = df[['name']].drop_duplicates()
selected_player = st.sidebar.selectbox("🎾 Player", ["All"] + player_df["name"].dropna().tolist())

search = st.sidebar.text_input("🔍 Search Player")

# ---------------- DATA FILTER ----------------

df = df[df["rank"] <= rank_limit]
df = df[df["points"] >= min_points]

if selected_country != "All":
    df = df[df["country"] == selected_country]

if selected_player != "All":
    df = df[df["name"] == selected_player]

if search:
    df = df[df["name"].str.contains(search, case=False)]

df = df.sort_values("rank")

# ---------------- KPIs ----------------
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎾 Players", len(df))
col2.metric("🌍 Countries", df["country"].nunique())
col3.metric("⭐ Avg Points", int(df["points"].mean()) if len(df)>0 else 0)
col4.metric("🔥 Max Points", int(df["points"].max()) if len(df)>0 else 0)

st.divider()

# ---------------- TOP PLAYERS ----------------
st.markdown("## 🏆 Top 10 Players")

top_df = df.head(10)

fig_top = px.bar(top_df, x="name", y="points", color="points", color_continuous_scale="viridis")
st.plotly_chart(fig_top, use_container_width=True)

# ---------------- BOTTOM PLAYERS ----------------
st.markdown("## 🔻 Bottom 10 Players")

bottom_df = df.tail(10)

fig_bottom = px.bar(bottom_df, x="name", y="points", color="points", color_continuous_scale="reds")
st.plotly_chart(fig_bottom, use_container_width=True)

st.divider()

# ---------------- COUNTRY ----------------
st.markdown("## 🌍 Country Participation")

country_data = df["country"].value_counts().reset_index()
country_data.columns = ["country", "players"]

fig_country = px.bar(country_data, x="country", y="players", color="players", color_continuous_scale="plasma")
st.plotly_chart(fig_country, use_container_width=True)

st.divider()

# ---------------- SCATTER ----------------
st.markdown("## 📊 Rank vs Points Insight")

fig_scatter = px.scatter(df, x="rank", y="points", color="points", size="points", hover_name="name")
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ---------------- BOX ----------------
fig_box = px.box(df, x="country", y="rank", color="country")
st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# ---------------- MAP ----------------
st.markdown("## 🌍 Global Player Distribution")

map_df = df["country"].value_counts().reset_index()
map_df.columns = ["country", "players"]

fig_map = px.choropleth(map_df, locations="country", locationmode="country names", color="players")
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ---------------- TREND ----------------
st.markdown("## 📈 Performance Trend")

trend_df = df.head(30)

fig_trend = px.line(trend_df, x="rank", y="points", markers=True)
st.plotly_chart(fig_trend, use_container_width=True)
