import os, sys, streamlit as st, pandas as pd
from nba_api.stats.static import teams
import data_fetcher as df

# --- Path fix for Streamlit Cloud ---
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

st.set_page_config(page_title="🏀 NBA Live Data Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Real Public Data Only")
st.markdown("""
This dashboard displays **real live and historical NBA data** fetched directly from  
- ESPN open JSON feeds (no auth keys)  
- NBA.com official stats (`nba_api`)   
All data is real‑time and public. No fallbacks or simulations.
""")

# -------------------------------
# TEAM SELECTION
# -------------------------------
try:
    team_map = {t["full_name"]: t["id"] for t in teams.get_teams()}
except Exception as e:
    st.error(f"Team list failed: {e}")
    team_map = {}

selected_team = st.sidebar.selectbox("Select an NBA Team", list(team_map.keys()) or [])
season = st.sidebar.text_input("Season (e.g. 2024‑25)", "2024‑25")

# -------------------------------
# 1. ESPN LIVE SCOREBOARD
# -------------------------------
st.subheader("🏟️ ESPN Live Scoreboard (Today)")
live_games = df.get_live_scoreboard()
if live_games.empty:
    st.info("No live or upcoming NBA games right now.")
else:
    st.dataframe(live_games, use_container_width=True)

# -------------------------------
# 2. RECENT TEAM GAMES (NBA.COM)
# -------------------------------
st.subheader(f"📊 Recent Games — {selected_team}")
team_id = team_map.get(selected_team)
if team_id:
    recent_games = df.get_team_recent_games(team_id, season)
    if not recent_games.empty:
        st.dataframe(recent_games, use_container_width=True)
    else:
        st.warning("No team data found.")
else:
    st.warning("Team selection error.")

# -------------------------------
# 3. HISTORICAL GAMES (ESPN)
# -------------------------------
st.subheader("📚 Recent NBA Final Scores (Last 7 Days, ESPN)")
hist = df.get_historical_games()
if hist.empty:
    st.warning("No past game results found for last week (check ESPN feed availability).")
else:
    st.dataframe(hist, use_container_width=True)

# -------------------------------
# FOOTER
# -------------------------------
st.caption("Live & historical data from ESPN open feed and NBA.com (`nba_api`). No API keys needed.")
