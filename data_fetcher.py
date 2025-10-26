import requests
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

# -------------------------------
# 1. Fetch Current ESPN Live Scoreboard
# -------------------------------
def get_live_scoreboard():
    """
    Fetch live or upcoming NBA games from ESPN's open API.
    Works without auth, showing current day's matchups, status, and scores.
    """
    url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json().get("events", [])
        games = []
        for event in data:
            competitors = event["competitions"][0]["competitors"]
            home = competitors[0] if competitors[0]["homeAway"] == "home" else competitors[1]
            away = competitors[1] if home == competitors[0] else competitors[0]
            games.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "status": event["status"]["type"]["description"],
                "start_time": event.get("date", "")[:19].replace("T", " "),
                "home_score": home.get("score", "0"),
                "away_score": away.get("score", "0")
            })
        return pd.DataFrame(games)
    except Exception as e:
        print("Error fetching ESPN scoreboard:", e)
        return pd.DataFrame()

# -------------------------------
# 2. Fetch Recent Games (Official NBA.com)
# -------------------------------
def get_team_recent_games(team_id, season="2024-25"):
    """
    Official NBA.com stats feed using nba_api.
    Returns recent 10 games for the selected team.
    """
    try:
        games = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id, season_nullable=season)
        df = games.get_data_frames()[0]
        df = df.head(10)[["GAME_DATE", "MATCHUP", "WL", "PTS", "REB", "AST", "PLUS_MINUS"]]
        return df
    except Exception as e:
        print("Error fetching NBA.com data:", e)
        return pd.DataFrame()

# -------------------------------
# 3. Fetch Historical Games (BallDontLie)
# -------------------------------
def get_historical_games(limit=15):
    """
    Pull real historical NBA game results from BallDontLie.io (no API key).
    """
    url = f"https://www.balldontlie.io/api/v1/games?per_page={limit}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json().get("data", [])
        games = [{
            "date": g["date"][:10],
            "home_team": g["home_team"]["full_name"],
            "away_team": g["visitor_team"]["full_name"],
            "home_score": g["home_team_score"],
            "away_score": g["visitor_team_score"],
            "status": g["status"]
        } for g in data]
        return pd.DataFrame(games)
    except Exception as e:
        print("Error fetching BallDontLie data:", e)
        return pd.DataFrame()
