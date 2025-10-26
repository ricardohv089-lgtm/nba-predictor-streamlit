import os, sys, requests, pandas as pd
from datetime import date, timedelta

# ensure importable from Streamlit Cloud
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


# -------------------------------
# 1. ESPN Live Scoreboard
# -------------------------------
def get_live_scoreboard():
    """Fetch live/upcoming NBA games from ESPN open feed."""
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
                "home_score": home.get("score", 0),
                "away_score": away.get("score", 0)
            })
        return pd.DataFrame(data)
    except Exception as e:
        print("ESPN live fetch error:", e)
        return pd.DataFrame()


# -------------------------------
# 2. Team Standings (Current Stats)
# -------------------------------
def get_team_standings(team_name: str = None):
    """Pull conference standings and team records from ESPN."""
    url = "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings"
    try:
        resp = requests.get(url, timeout=10).json()
        teams = []
        for group in resp.get("children", []):  # East / West
            for entry in group["standings"]["entries"]:
                t = entry["team"]
                stats = {s["name"]: s.get("value") for s in entry["stats"]}
                teams.append({
                    "TEAM": t["displayName"],
                    "W": stats.get("wins", 0),
                    "L": stats.get("losses", 0),
                    "WIN_PCT": stats.get("winPercent", 0),
                    "GB": stats.get("gamesBehind", 0),
                    "CONF_RANK": stats.get("rankConf", 0),
                    "STREAK": stats.get("streak", "")
                })
        df = pd.DataFrame(teams)
        return df if not team_name else df[df["TEAM"].str.contains(team_name, case=False)]
    except Exception as e:
        print("Standings fetch error:", e)
        return pd.DataFrame()


# -------------------------------
# 3. Historical Scores (past 7 days)
# -------------------------------
def get_historical_games(days_back=7):
    """Real previous‑week results using ESPN’s public JSON."""
    today = date.today()
    records = []
    try:
        for i in range(1, days_back + 1):
            query = (today - timedelta(days=i)).strftime("%Y%m%d")
            url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={query}"
            resp = requests.get(url, timeout=10)
            for ev in resp.json().get("events", []):
                comp = ev["competitions"][0]
                home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
                away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
                records.append({
                    "date": query,
                    "home_team": home["team"]["displayName"],
                    "away_team": away["team"]["displayName"],
                    "home_score": home.get("score", 0),
                    "away_score": away.get("score", 0),
                    "status": ev["status"]["type"]["description"]
                })
        return pd.DataFrame(records)
    except Exception as e:
        print("Historical ESPN fetch error:", e)
        return pd.DataFrame()
