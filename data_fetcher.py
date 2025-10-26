import os, sys, requests, pandas as pd
from datetime import date, timedelta
from nba_api.stats.endpoints import leaguedashteamstats

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# -------------------------------
# 1. ESPN Live Scoreboard
# -------------------------------
def get_live_scoreboard():
    """Fetch live/upcoming NBA matchups (key‑free public ESPN feed)."""
    url = "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        resp = requests.get(url, timeout=10)
        events = resp.json().get("events", [])
        games = []
        for e in events:
            comp = e["competitions"][0]
            home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
            away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
            games.append({
                "home_team": home["team"]["displayName"],
                "away_team": away["team"]["displayName"],
                "status": e["status"]["type"]["description"],
                "start_time": e["date"][:19].replace("T", " "),
                "home_score": home.get("score", 0),
                "away_score": away.get("score", 0)
            })
        return pd.DataFrame(games)
    except Exception as e:
        print("ESPN fetch error:", e)
        return pd.DataFrame()

# -------------------------------
# 2. Team Stats – safer substitute for LeagueGameFinder
# -------------------------------
def get_team_recent_games(team_id, season="2024-25"):
    """
    NBA.com /stats endpoints changed in 2025 causing LeagueGameFinder errors.
    This backup uses leaguedashteamstats to show team averages instead
    of per‑game log until the API is restored.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://stats.nba.com/",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true"
    }
    try:
        data = leaguedashteamstats.LeagueDashTeamStats(
            per_mode_detailed="PerGame",
            season=season,
            headers=headers
        ).get_data_frames()[0]
        team_row = data[data["TEAM_ID"] == team_id]
        if team_row.empty:
            return pd.DataFrame([{"Info": "No team data available (right now NBA.com may be limiting requests)."}])
        cols = ["TEAM_NAME", "GP", "W", "L", "MIN", "PTS", "REB", "AST", "TOV", "PLUS_MINUS"]
        return team_row[cols].reset_index(drop=True)
    except Exception as e:
        print("NBA team stats fallback error:", e)
        return pd.DataFrame([{"Info": f"NBA team stats unavailable ({e})"}])

# -------------------------------
# 3. Historical Scores (ESPN past 7 days)
# -------------------------------
def get_historical_games(days_back=7):
    """Real previous‑week results using ESPN’s public JSON API (no keys)."""
    today = date.today()
    records = []
    try:
        for i in range(1, days_back + 1):
            query = (today - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={query}"
            resp = requests.get(url, timeout=10)
            events = resp.json().get("events", [])
            for e in events:
                comp = e["competitions"][0]
                home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
                away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
                records.append({
                    "date": query,
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score", 0),
                    "away_score": away.get("score", 0),
                    "status": e["status"]["type"]["description"]
                })
        return pd.DataFrame(records)
    except Exception as e:
        print("Historical ESPN fetch error:", e)
        return pd.DataFrame()
