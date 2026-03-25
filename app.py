import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Tennis Pro Dashboard", layout="wide")

engine = create_engine("postgresql+psycopg2://postgres:postgres123@localhost:5432/tennis_data")

# ---------------- TITLE ----------------

st.markdown("<h1 style='text-align:center;color:#6C63FF;'>🎾 Tennis Pro Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:gray;'>Player Rankings | Country Insights | Performance Trends</h4>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Dashboard Controls")

rank_limit = st.sidebar.slider("Max Rank", 1, 500, 100)
min_points = st.sidebar.slider("Min Points", 0, 10000, 0)

# Country filter

country_df = pd.read_sql("SELECT DISTINCT country FROM competitors", engine)
selected_country = st.sidebar.selectbox("🌍 Country", ["All"] + country_df["country"].dropna().tolist())

# Player filter

player_df = pd.read_sql("SELECT name FROM competitors", engine)
selected_player = st.sidebar.selectbox("🎾 Player", ["All"] + player_df["name"].dropna().tolist())
search = st.sidebar.text_input("🔍 Search Player")

# Venue filter

venue_df = pd.read_sql("SELECT DISTINCT country_name FROM venues", engine)
selected_venue = st.sidebar.selectbox("🏟 Venue Country", ["All"] + venue_df["country_name"].dropna().tolist())

# Competition filter (if table exists)

# Competition filter (SAFE VERSION)

comp_df = pd.read_sql("SELECT DISTINCT competition_name FROM competitions", engine)

selected_comp = st.sidebar.selectbox(
    "🏆 Competition",
    ["All"] + comp_df["competition_name"].dropna().tolist()
)

# ---------------- DATA ----------------

query = f"""
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN competitor_rankings r
ON c.competitor_id = r.competitor_id
WHERE r.rank <= {rank_limit}
AND r.points >= {min_points}
"""

df = pd.read_sql(query, engine)

df = df[df["country"] == selected_country] if selected_country != "All" else df
df = df[df["name"] == selected_player] if selected_player != "All" else df
df = df[df["name"].str.contains(search, case=False)] if search else df

df = df.sort_values("rank")

# ---------------- KPIs ----------------

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎾 Players", len(df))
col2.metric("🌍 Countries", df["country"].nunique())
col3.metric("⭐ Avg Points", int(df["points"].mean()) if len(df)>0 else 0)
col4.metric("🔥 Max Points", int(df["points"].max()) if len(df)>0 else 0)

st.divider()

# ---------------- TOP PLAYERS CHART ----------------

st.markdown("## 🏆 Top 10 Players")

top_df = df.head(10)

fig_top = px.bar(
top_df,
x="name",
y="points",
color="points",
color_continuous_scale="viridis",
title="Top Players by Points"
)

st.plotly_chart(fig_top, use_container_width=True)

# ---------------- BOTTOM PLAYERS CHART ----------------

st.markdown("## 🔻 Bottom 10 Players")

bottom_df = df.tail(10)

fig_bottom = px.bar(
bottom_df,
x="name",
y="points",
color="points",
color_continuous_scale="reds",
title="Lowest Ranked Players"
)

st.plotly_chart(fig_bottom, use_container_width=True)

st.divider()

# ---------------- COUNTRY ANALYSIS ----------------

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

st.divider()

# ---------------- RANK DISTRIBUTION ----------------

st.markdown("## 📊 Rank vs Points Insight")

# Scatter (BEST visualization 🔥)

fig_scatter = px.scatter(
df,
x="rank",
y="points",
color="points",
size="points",
hover_name="name",
color_continuous_scale="viridis",
title="Rank vs Points Relationship"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# Box plot (distribution clarity)

fig_box = px.box(
df,
x="country",
y="rank",
color="country",
title="Rank Distribution by Country"
)

st.plotly_chart(fig_box, use_container_width=True)


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

st.divider()

# ---------------- TREND ----------------

st.markdown("## 📈 Performance Trend (Forecast View)")

trend_df = df.head(30)

fig_trend = px.line(
trend_df,
x="rank",
y="points",
markers=True,
title="Points vs Rank Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)
