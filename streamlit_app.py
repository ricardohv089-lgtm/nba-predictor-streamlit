import streamlit as st
import pandas as pd
from data_fetcher import get_team_recent_games, get_live_odds

st.set_page_config(page_title="🏀 NBA Predictor Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Live Data Dashboard")

st.markdown("### Step 1: View current NBA data fetched directly from APIs")

# --- Team ID picker ---
team_map = {
    "Boston Celtics": "1610612738",
    "Los Angeles Lakers": "1610612747",
    "Golden State Warriors": "1610612744",
    "Milwaukee Bucks": "1610612749"
}

selected_team = st.selectbox("Select a Team", list(team_map.keys()))
season = st.text_input("Season format: e.g. 2024-25", "2024-25")

# --- Fetch team games ---
with st.spinner("Fetching recent team games..."):
    team_games = get_team_recent_games(team_map[selected_team], season)

if not team_games.empty:
    st.dataframe(team_games.head(10))
else:
    st.warning("No data retrieved — check season format or API connectivity.")

# --- Fetch live odds ---
st.markdown("### Step 2: Live Game Odds")
try:
    nba_odds = get_live_odds()
    if nba_odds:
        odds_df = pd.json_normalize(nba_odds)
        st.dataframe(odds_df[["home_team", "away_team", "bookmakers"]].head(10))
    else:
        st.warning("No live odds available at the moment.")
except Exception as e:
    st.error(f"Error retrieving odds: {e}")

st.info("✅ Next step: we'll connect predictions from trained ML models.")
