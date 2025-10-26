import os, sys, pandas as pd, streamlit as st
from nba_api.stats.static import teams
import data_fetcher as df

sys.path.append(os.path.dirname(__file__))
st.set_page_config(page_title="🏀 NBA Public Stats Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Live & Historical Public Data Feeds")
st.markdown("""
All data comes from  
- **ESPN open JSON scoreboards** for live and recent results  
- **NBA.com official team stats** (`nba_api` backup mode)  
100 % real and key‑free.
""")

# -------------------------------
# TEAM SELECTOR
# -------------------------------
try:
    team_map = {t["full_name"]: t["id"] for t in teams.get_teams()}
except Exception as e:
    st.error(f"Failed to load teams: {e}")
    team_map = {}

selected_team = st.sidebar.selectbox("Select team:", list(team_map.keys()) or [])
season = st.sidebar.text_input("Season (e.g. 2024‑25)", "2024‑25")
team_id = team_map.get(selected_team)

# -------------------------------
# TODAY’S LIVE GAMES (ESPN)
# -------------------------------
st.subheader("🏟️ Today's NBA Games — Live/Upcoming (ESPN)")
live = df.get_live_scoreboard()
st.dataframe(live if not live.empty else pd.DataFrame([{"Info": "No live or upcoming matches now."}]),
             use_container_width=True)

# -------------------------------
# TEAM STATS (NBA.com, Fallback Safe)
# -------------------------------
st.subheader(f"📊 {selected_team} — Team Stats (Averages Per Game)")
if not team_id:
    st.warning("Select a valid team.")
else:
    team_data = df.get_team_recent_games(team_id, season)
    st.dataframe(team_data, use_container_width=True)

# -------------------------------
# PAST WEEK FINAL SCORES (ESPN)
# -------------------------------
st.subheader("📚 Recent Final Scores (Last 7 Days — ESPN)")
history = df.get_historical_games()
st.dataframe(history if not history.empty else pd.DataFrame([{"Info": "No recent final scores available."}]),
             use_container_width=True)

st.caption("Public ESPN and NBA.com feeds (auto fallback if blocked). No API keys or simulations.")
