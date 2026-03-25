import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tennis Pro Dashboard", layout="wide")

# ---------------- DARK THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #1c1f26;
}
h1, h2, h3, h4 {
    color: #6C63FF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>🎾 Tennis Pro Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:gray;'>Player Rankings | Country Insights | Performance Trends</h4>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_json("double_competitors_rankings.json")
df = pd.json_normalize(df)

# Fix column names
df.columns = [col.lower().replace(".", "_") for col in df.columns]

# Rename columns safely
if "competitor_name" in df.columns:
    df = df.rename(columns={"competitor_name": "name"})
if "competitor_country" in df.columns:
    df = df.rename(columns={"competitor_country": "country"})

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🎛 Dashboard Controls")

rank_limit = st.sidebar.slider("Max Rank", 1, 500, 100)
min_points = st.sidebar.slider("Min Points", 0, 10000, 0)

# Filters
country_df = df[['country']].drop_duplicates() if "country" in df.columns else pd.DataFrame({"country":[]})
selected_country = st.sidebar.selectbox("🌍 Country", ["All"] + country_df["country"].dropna().tolist())

player_df = df[['name']].drop_duplicates() if "name" in df.columns else pd.DataFrame({"name":[]})
selected_player = st.sidebar.selectbox("🎾 Player", ["All"] + player_df["name"].dropna().tolist())

search = st.sidebar.text_input("🔍 Search Player")

# ---------------- DATA FILTER ----------------
if "rank" in df.columns:
    df = df[df["rank"] <= rank_limit]

if "points" in df.columns:
    df = df[df["points"] >= min_points]

if selected_country != "All" and "country" in df.columns:
    df = df[df["country"] == selected_country]

if selected_player != "All" and "name" in df.columns:
    df = df[df["name"] == selected_player]

if search and "name" in df.columns:
    df = df[df["name"].str.contains(search, case=False, na=False)]

df = df.sort_values("rank") if "rank" in df.columns else df

# ---------------- KPIs ----------------
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎾 Players", len(df))
col2.metric("🌍 Countries", df["country"].nunique() if "country" in df.columns else 0)
col3.metric("⭐ Avg Points", int(df["points"].mean()) if "points" in df.columns and len(df)>0 else 0)
col4.metric("🔥 Max Points", int(df["points"].max()) if "points" in df.columns and len(df)>0 else 0)

st.markdown("---")

# ---------------- TOP PLAYERS ----------------
st.markdown("## 🏆 Top 10 Players")

top_df = df.head(10)

if "name" in df.columns and "points" in df.columns:
    fig_top = px.bar(top_df, x="name", y="points", color="points")
    st.plotly_chart(fig_top, use_container_width=True)

# ---------------- BOTTOM PLAYERS ----------------
st.markdown("## 🔻 Bottom 10 Players")

bottom_df = df.tail(10)

if "name" in df.columns and "points" in df.columns:
    fig_bottom = px.bar(bottom_df, x="name", y="points", color="points")
    st.plotly_chart(fig_bottom, use_container_width=True)

st.markdown("---")

# ---------------- COUNTRY ----------------
st.markdown("## 🌍 Country Participation")

if "country" in df.columns:
    country_data = df["country"].value_counts().reset_index()
    country_data.columns = ["country", "players"]

    fig_country = px.bar(country_data, x="country", y="players", color="players")
    st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# ---------------- SCATTER ----------------
st.markdown("## 📊 Rank vs Points Insight")

if "rank" in df.columns and "points" in df.columns:
    fig_scatter = px.scatter(df, x="rank", y="points", color="points", size="points", hover_name="name")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ---------------- BOX ----------------
if "country" in df.columns and "rank" in df.columns:
    fig_box = px.box(df, x="country", y="rank", color="country")
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ---------------- MAP ----------------
st.markdown("## 🌍 Global Player Distribution")

if "country" in df.columns:
    map_df = df["country"].value_counts().reset_index()
    map_df.columns = ["country", "players"]

    fig_map = px.choropleth(map_df, locations="country", locationmode="country names", color="players")
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ---------------- TREND ----------------
st.markdown("## 📈 Performance Trend")

if "rank" in df.columns and "points" in df.columns:
    trend_df = df.head(30)

    fig_trend = px.line(trend_df, x="rank", y="points", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)
