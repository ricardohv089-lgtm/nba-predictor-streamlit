import os, sys, pandas as pd
from datetime import date, timedelta
import requests
from data_saver import collect_season_data

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# -------------------------------
# Live / Past Week ESPN Feeds
# -------------------------------
def get_live_scoreboard():
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
                "start_time": e["date"][:19].replace("T", " "),
                "status": e["status"]["type"]["description"],
                "home_score": home.get("score", 0),
                "away_score": away.get("score", 0)
            })
        return pd.DataFrame(games)
    except Exception as e:
        print("ESPN fetch error:", e)
        return pd.DataFrame()

def get_historical_games(days_back=7):
    today = date.today()
    all_games = []
    try:
        for i in range(1, days_back + 1):
            d = (today - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d}"
            resp = requests.get(url, timeout=10)
            for e in resp.json().get("events", []):
                comp = e["competitions"][0]
                home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
                away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
                all_games.append({
                    "date": d,
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score", 0),
                    "away_score": away.get("score", 0),
                    "status": e["status"]["type"]["description"]
                })
        return pd.DataFrame(all_games)
    except Exception as e:
        print("Historical fetch error:", e)
        return pd.DataFrame()
