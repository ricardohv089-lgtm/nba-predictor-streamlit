import os, sys, requests, pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# --- Ensure module can always be found (both locally & on Streamlit Cloud)
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# -------------------------------
# 1. ESPN Live Scoreboard (public)
# -------------------------------
def get_live_scoreboard():
    """Fetch real or upcoming NBA matchups from ESPN's open API."""
    url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        events = resp.json().get("events", [])
        games = []
        for evt in events:
            comp = evt["competitions"][0]
            home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
            away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
            games.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "status": evt["status"]["type"]["description"],
                "start_time": evt["date"][:19].replace("T", " "),
                "home_score": home.get("score", 0),
                "away_score": away.get("score", 0)
            })
        return pd.DataFrame(games)
    except Exception as e:
        print("ESPN fetch error:", e)
        return pd.DataFrame()

# -------------------------------
# 2. NBA.com official data
# -------------------------------
def get_team_recent_games(team_id, season="2024-25"):
    """Return last 10 games for given team from NBA.com stats feed."""
    try:
        df = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season
        ).get_data_frames()[0]
        needed = ["GAME_DATE", "MATCHUP", "WL", "PTS", "REB", "AST", "PLUS_MINUS"]
        return df.head(10)[needed]
    except Exception as e:
        print("NBA.com fetch error:", e)
        return pd.DataFrame()

# -------------------------------
# 3. BallDontLie Historical
# -------------------------------
def get_historical_games(limit=20):
    """Pull real historical NBA games from BallDontLie.io."""
    url = f"https://www.balldontlie.io/api/v1/games?per_page={limit}"
    try:
        res = requests.get(url, timeout=10)
        games = [{
            "date": g["date"][:10],
            "home_team": g["home_team"]["full_name"],
            "away_team": g["visitor_team"]["full_name"],
            "home_score": g["home_team_score"],
            "away_score": g["visitor_team_score"],
            "status": g["status"]
        } for g in res.json().get("data", [])]
        return pd.DataFrame(games)
    except Exception as e:
        print("BallDontLie fetch error:", e)
        return pd.DataFrame()
