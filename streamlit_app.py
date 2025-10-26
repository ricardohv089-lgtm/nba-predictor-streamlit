import os, sys, streamlit as st, pandas as pd
import data_fetcher as df

sys.path.append(os.path.dirname(__file__))
st.set_page_config(page_title="🏀 NBA Public Data Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Real Data Only (ESPN Feeds)")
st.markdown("""
Displays **live games**, **team records**, and **last‑week results** directly from  
**ESPN’s open API** — no keys, no simulation, fully public and real.  
""")

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.header("Filter options")
team_input = st.sidebar.text_input("Filter by team name (optional):", "")
days_back = st.sidebar.slider("Past Days for History", 3, 10, 7)

# -------------------------------
# 1. Live Games (Today)
# -------------------------------
st.subheader("🏟️ Live / Upcoming Games — ESPN")
live_df = df.get_live_scoreboard()
st.dataframe(live_df if not live_df.empty else pd.DataFrame([{"Info": "No live or upcoming games listed."}]),
             use_container_width=True)

# -------------------------------
# 2. Team Standings – Current Stats
# -------------------------------
st.subheader("📊 Team Records (Conference Standings – ESPN)")
team_df = df.get_team_standings(team_input) if team_input else df.get_team_standings()
st.dataframe(team_df if not team_df.empty else pd.DataFrame([{"Info": "No standings found or connection issue."}]),
             use_container_width=True)

# -------------------------------
# 3. Historical Results (last 7 days)
# -------------------------------
st.subheader("📚 Final Scores – Last Week (ESPN)")
hist = df.get_historical_games(days_back)
st.dataframe(hist if not hist.empty else pd.DataFrame([{"Info": "No recent final scores."}]),
             use_container_width=True)

st.caption("Data from ESPN public JSON feed – official results mirroring ESPN.com scoreboards.")
