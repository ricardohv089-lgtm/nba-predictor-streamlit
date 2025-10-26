import os, sys, pandas as pd, streamlit as st
from nba_api.stats.static import teams
import data_fetcher as df

# --- Fix import path for Streamlit Cloud
sys.path.append(os.path.dirname(__file__))

st.set_page_config(page_title="🏀 NBA Public Data Dashboard", layout="wide")
st.title("🏀 NBA Prediction System — 100 % Public Real Data")
st.markdown("""
Displays **live games**, **recent team performance**, and **past week final scores**
using ESPN public feeds and NBA.com official stats — no API keys or simulations.
""")

# -------------------------------
# TEAM SELECTOR (NBA.com Official)
# -------------------------------
try:
    team_map = {t["full_name"]: t["id"] for t in teams.get_teams()}
except Exception as e:
    st.error(f"Failed to load teams: {e}")
    team_map = {}

selected_team = st.sidebar.selectbox("Choose a team", list(team_map.keys()) or ["None"])
season = st.sidebar.text_input("Season (e.g. 2024‑25)", "2024‑25")

# -------------------------------
# LIVE SCOREBOARD (ESPN)
# -------------------------------
st.subheader("🏟️ Today’s ESPN Scoreboard")
live_df = df.get_live_scoreboard()
if live_df.empty:
    st.info("No live or upcoming NBA games right now.")
else:
    st.dataframe(live_df, use_container_width=True)

# -------------------------------
# RECENT TEAM GAMES (NBA.com)
# -------------------------------
st.subheader(f"📊 Recent Games — {selected_team}")
team_id = team_map.get(selected_team)
if not team_id:
    st.warning("Select a valid team.")
else:
    team_df = df.get_team_recent_games(team_id, season)
    if team_df.empty:
        st.info("No results returned for this team or season — NBA.com may be blocking requests.")
    else:
        st.dataframe(team_df, use_container_width=True)

# -------------------------------
# HISTORICAL (Last 7 Days ESPN)
# -------------------------------
st.subheader("📚 Final Scores — Last 7 Days (ESPN)")
hist_df = df.get_historical_games()
if hist_df.empty:
    st.info("No past week results found — try again later when ESPN updates their feed.")
else:
    st.dataframe(hist_df, use_container_width=True)

st.caption("Data sources: NBA.com & ESPN public feeds (official, no auth required).")
