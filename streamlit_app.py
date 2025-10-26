import streamlit as st
import pandas as pd
from nba_api.stats.static import teams
from data_fetcher import get_team_recent_games, get_live_odds

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="🏀 NBA Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏀 NBA Prediction System — Live Data Dashboard")
st.markdown(
    """
    This dashboard fetches **real NBA data** directly from the official NBA.com API 
    and **live betting odds** from The Odds API.  
    Use this to explore team stats and market data in real time.
    """
)

# -------------------------------
# TEAM SELECTION (Auto Loads All 30 Teams)
# -------------------------------
st.sidebar.header("Select Team and Season")

try:
    team_map = {team['full_name']: team['id'] for team in teams.get_teams()}
except Exception as e:
    st.error(f"Error loading team list: {e}")
    team_map = {}

selected_team = st.sidebar.selectbox(
    "Choose an NBA Team:",
    list(team_map.keys()) if team_map else ["Error loading teams"]
)

season = st.sidebar.text_input("Enter Season (e.g. 2024-25):", "2024-25")

# -------------------------------
# RECENT TEAM GAMES
# -------------------------------
st.subheader(f"📊 Recent Games — {selected_team}")
with st.spinner("Fetching recent team games from NBA.com..."):
    try:
        if team_map:
            team_games = get_team_recent_games(team_map[selected_team], season)
            if not team_games.empty:
                st.dataframe(
                    team_games.head(10),
                    use_container_width=True
                )
            else:
                st.warning("No games found for this team or season.")
        else:
            st.warning("Team list failed to load.")
    except Exception as e:
        st.error(f"Failed to fetch NBA game data: {e}")

# -------------------------------
# LIVE ODDS (Moneyline, Spread, Totals)
# -------------------------------
st.subheader("💰 Live NBA Game Odds")
st.markdown("*(Fetched from The Odds API — requires you to insert your free API key in data_fetcher.py)*")

try:
    odds_data = get_live_odds()
    if odds_data:
        odds_df = pd.json_normalize(odds_data)
        display_cols = [
            "home_team",
            "away_team",
            "commence_time",
            "sport_key"
        ]
        st.dataframe(
            odds_df[display_cols].head(10),
            use_container_width=True
        )
    else:
        st.warning("No odds available right now — happens when no active or upcoming NBA games are found.")
except Exception as e:
    st.error(f"Error retrieving odds: {e}")

# -------------------------------
# NEXT STEP HINT
# -------------------------------
st.info("""
✅ **Next Step:** Add machine learning predictions for Moneyline, Spread, and Totals.

- We'll load trained XGBoost and LightGBM models.
- Predictions will appear directly beside live odds.
- Accuracy target: ~70% ML / 57% Spread / 55% Totals based on current benchmarks.
""")
