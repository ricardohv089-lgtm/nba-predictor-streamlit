import os, sys, requests, pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import leaguegamefinder

# --- Ensure Streamlit can locate this local module
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# -------------------------------
# 1. ESPN Live Scoreboard (Today)
# -------------------------------
def get_live_scoreboard():
    """Fetch live or upcoming NBA matchups from ESPN's open JSON feed."""
    url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        events = resp.json().get("events", [])
        data = []
        for e in events:
            comp = e["competitions"][0]
            home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
            away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
            data.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "status": e["status"]["type"]["description"],
                "start_time": e["date"][:19].replace("T", " "),
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0")
            })
        return pd.DataFrame(data)
    except Exception as e:
        print("ESPN live fetch error:", e)
        return pd.DataFrame()

# -------------------------------
# 2. NBA.com Official Recent Games
# -------------------------------
def get_team_recent_games(team_id, season="2024-25"):
    """
    Return last 10 regular‑season games for a given NBA team.
    Sometimes nba_api endpoints get blocked; handle gracefully.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://stats.nba.com/",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true"
    }
    try:
        games = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season
        )
        df = games.get_data_frames()[0]
        if df.empty:
            return pd.DataFrame([{"Info": "No official results available for this team/season"}])
        cols = ["GAME_DATE", "MATCHUP", "WL", "PTS", "REB", "AST", "PLUS_MINUS"]
        return df.head(10)[cols]
    except Exception as e:
        print("NBA.com fetch error:", e)
        return pd.DataFrame([{"Info": f"Error: {e}"}])

# -------------------------------
# 3. ESPN Historical Games (Last 7 Days)
# -------------------------------
def get_historical_games(days_back=7):
    """Pull prior‑week NBA final scores via ESPN's public JSON API."""
    today = date.today()
    records = []
    try:
        for i in range(1, days_back + 1):
            d_str = (today - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d_str}"
            resp = requests.get(url, timeout=10)
            events = resp.json().get("events", [])
            for e in events:
                comp = e["competitions"][0]
                home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
                away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
                records.append({
                    "date": d_str,
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score", "0"),
                    "away_score": away.get("score", "0"),
                    "status": e["status"]["type"]["description"]
                })
        return pd.DataFrame(records)
    except Exception as e:
        print("ESPN historical fetch error:", e)
        return pd.DataFrame()
