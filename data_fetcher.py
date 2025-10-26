import os, sys, requests, pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import leaguegamefinder

# Ensure local imports always work both locally and on Streamlit Cloud
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# -------------------------------
# 1. ESPN Live Scoreboard (current & upcoming)
# -------------------------------
def get_live_scoreboard():
    """Fetch all live or upcoming NBA matchups from ESPN's public API."""
    url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        events = resp.json().get("events", [])
        games = []
        for evt in events:
            comp = evt["competitions"][0]
            home = [c for c in comp["competitors"] if c["homeAway"] == "home"][0]
            away = [c for c in comp["competitors"] if c["homeAway"] == "away"][0]
            games.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "status": evt["status"]["type"]["description"],
                "start_time": evt["date"][:19].replace("T", " "),
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0")
            })
        return pd.DataFrame(games)
    except Exception as e:
        print("Error fetching ESPN scoreboard:", e)
        return pd.DataFrame()

# -------------------------------
# 2. Recent Team Games (NBA.com official)
# -------------------------------
def get_team_recent_games(team_id, season="2024-25"):
    """Return last 10 regular‑season games for a given NBA team."""
    try:
        games = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season
        ).get_data_frames()[0]
        cols = ["GAME_DATE", "MATCHUP", "WL", "PTS", "REB", "AST", "PLUS_MINUS"]
        return games.head(10)[cols]
    except Exception as e:
        print("NBA.com error:", e)
        return pd.DataFrame()

# -------------------------------
# 3. Historical Games (ESPN – past X days)
# -------------------------------
def get_historical_games(days_back=7):
    """
    Fetch final NBA results from the previous week using ESPN's public API.
    Each call retrieves daily scoreboards for the last `days_back` days.
    """
    try:
        today = date.today()
        records = []
        for i in range(1, days_back + 1):
            query_date = (today - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={query_date}"
            resp = requests.get(url, timeout=10)
            events = resp.json().get("events", [])
            for evt in events:
                comp = evt["competitions"][0]
                home = [c for c in comp["competitors"] if c["homeAway"] == "home"][0]
                away = [c for c in comp["competitors"] if c["homeAway"] == "away"][0]
                records.append({
                    "date": query_date,
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score", "0"),
                    "away_score": away.get("score", "0"),
                    "status": evt["status"]["type"]["description"]
                })
        return pd.DataFrame(records)
    except Exception as e:
        print("Error fetching historical ESPN data:", e)
        return pd.DataFrame()
