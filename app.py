import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="Tennis Analytics Dashboard",
    layout="wide"
)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------

engine = create_engine(
    "postgresql+psycopg2://postgres:post#@localhost:5432/tennis_data"
)

st.title("🎾 Tennis Rankings Explorer")

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("🎛 Dashboard Filters")

rank_limit = st.sidebar.slider(
    "Maximum Rank",
    1,
    500,
    50
)

min_points = st.sidebar.slider(
    "Minimum Points",
    0,
    10000,
    1000
)

country_list = pd.read_sql(
    "SELECT DISTINCT country FROM competitors ORDER BY country",
    engine
)

selected_country = st.sidebar.selectbox(
    "Country",
    ["All"] + country_list["country"].tolist()
)

top_n = st.sidebar.slider(
    "Top Players Chart Size",
    5,
    20,
    10
)

sort_option = st.sidebar.selectbox(
    "Sort Rankings By",
    ["Rank", "Points"]
)

search_player = st.sidebar.text_input(
    "Search Competitor"
)

# -----------------------------
# LOAD DATA
# -----------------------------

query = f"""
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN competitor_rankings r
ON c.competitor_id = r.competitor_id
WHERE r.rank <= {rank_limit}
AND r.points >= {min_points}
"""

df = pd.read_sql(query, engine)

# Apply filters safely

if selected_country != "All":
    df = df[df["country"] == selected_country]

if search_player:
    df = df[df["name"].str.contains(search_player, case=False)]

if sort_option == "Rank":
    df = df.sort_values("rank")
else:
    df = df.sort_values("points", ascending=False)

# -----------------------------
# SAFETY CHECK
# -----------------------------

if df.empty:
    st.warning("No players found for the selected filters. Please adjust filters.")
    st.stop()

# -----------------------------
# KPI CARDS
# -----------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Players Loaded", len(df))
col2.metric("Average Points", int(df["points"].mean()) if not df.empty else 0)
col3.metric("Highest Points", int(df["points"].max()) if not df.empty else 0)

st.divider()

# -----------------------------
# TOP PLAYER HIGHLIGHT
# -----------------------------

top_player = df.iloc[0] if not df.empty else None

if top_player is not None:

    st.subheader("🌟 Current Top Ranked Player")

    st.info(
        f"""
Player: **{top_player['name']}**

Country: **{top_player['country']}**

Rank: **{top_player['rank']}**

Points: **{top_player['points']}**
"""
    )

st.divider()

# -----------------------------
# RANKINGS TABLE + CHART
# -----------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏆 Rankings Table")
    st.dataframe(df, use_container_width=True)

with col2:

    st.subheader("Top Players by Points")

    top_players = df.head(min(top_n, len(df)))

    fig = px.bar(
        top_players,
        x="name",
        y="points",
        color="points",
        color_continuous_scale="viridis"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# -----------------------------
# COUNTRY ANALYSIS
# -----------------------------

st.subheader("🌍 Player Distribution by Country")

country_query = """
SELECT country, COUNT(*) as players
FROM competitors
GROUP BY country
ORDER BY players DESC
LIMIT 10
"""

country_df = pd.read_sql(country_query, engine)

fig2 = px.bar(
    country_df,
    x="country",
    y="players",
    color="players",
    color_continuous_scale="plasma"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# -----------------------------
# RANK DISTRIBUTION
# -----------------------------

st.subheader("📈 Rank Distribution")

fig3 = px.histogram(
    df,
    x="rank",
    nbins=25,
    color_discrete_sequence=["#4B4146"]
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# -----------------------------
# VENUE ANALYSIS
# -----------------------------

st.subheader("🏟 Venue Distribution")

venue_query = """
SELECT country_name, COUNT(*) as venues
FROM venues
GROUP BY country_name
ORDER BY venues DESC
LIMIT 10
"""

venue_df = pd.read_sql(venue_query, engine)

fig4 = px.pie(
    venue_df,
    names="country_name",
    values="venues",
    title="Venues by Country"
)

st.plotly_chart(fig4, use_container_width=True)


# -----------------------------
# WORLD MAP OF PLAYERS
# -----------------------------

st.divider()

st.subheader("🌍 Global Player Distribution")

map_query = """
SELECT country, COUNT(*) as players
FROM competitors
GROUP BY country
"""

map_df = pd.read_sql(map_query, engine)

# Convert country names to uppercase for better mapping
map_df["country"] = map_df["country"].str.upper()

fig_map = px.choropleth(
    map_df,
    locations="country",
    locationmode="country names",
    color="players",
    color_continuous_scale="Blues",
    title="Tennis Players by Country"
)

st.plotly_chart(fig_map, use_container_width=True)