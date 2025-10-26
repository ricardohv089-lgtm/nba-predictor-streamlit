import os, sys, streamlit as st, pandas as pd
from nba_api.stats.static import teams
import data_fetcher as df

# --- Ensure same folder imports work on Streamlit Cloud ---
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

st.set_page_config(page_title="🏀 NBA Live Data Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Real Public Data")
st.markdown("""
View official **NBA.com**, **ESPN**, and **BallDontLie** statistics — all fetched live with no keys or simulation data.
""")

# -------------------------------
# Team selector
# -------------------------------
try:
    team_map = {t["full_name"]: t["id"] for t in teams.get_teams()}
except Exception as e:
    st.error(f"Team list failed: {e}")
    team_map = {}

selected_team = st.sidebar.selectbox("Choose a team:", list(team_map.keys()) or [])
season = st.sidebar.text_input("Season (e.g. 2024-25)", "2024-25")

# -------------------------------
# ESPN Live Games
# -------------------------------
st.subheader("🏟️ ESPN Live Scoreboard (Today)")
live_games = df.get_live_scoreboard()
if live_games.empty:
    st.info("No live or upcoming games found right now.")
else:
    st.dataframe(live_games, use_container_width=True)

# -------------------------------
# Recent Team Games (NBA.com)
# -------------------------------
st.subheader(f"📊 {selected_team} — Last 10 Games (NBA.com Official Data)")
team_id = team_map.get(selected_team)
if team_id:
    team_recent = df.get_team_recent_games(team_id, season)
    st.dataframe(team_recent, use_container_width=True)
else:
    st.warning("No team selected or load error.")

# -------------------------------
# Historical Games (BallDontLie)
# -------------------------------
st.subheader("📚 Historical NBA Games (BallDontLie Public API)")
history = df.get_historical_games()
if not history.empty:
    st.dataframe(history, use_container_width=True)
else:
    st.info("No historical data returned right now.")

# -------------------------------
# Footer
# -------------------------------
st.caption("Live public data sourced from ESPN, NBA.com & BallDontLie (no API keys, no static info).")
