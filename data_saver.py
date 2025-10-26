import os, requests, pandas as pd
from datetime import datetime, timedelta

# Path to permanent /data folder in repo
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def collect_season_data(seasons_back=5):
    """
    Collect NBA games from ESPN JSON API for past N seasons.
    Saves complete dataset to ./data/nba_games_5yr.csv (no row truncation).
    """
    all_games = []
    today = datetime.today()
    start_year = today.year - seasons_back

    try:
        for season in range(start_year, today.year + 1):
            print(f"Fetching season {season}-{season+1} ...")
            start = datetime(season, 10, 1)
            end = datetime(season + 1, 7, 1)
            date = start
            while date <= end:
                date_str = date.strftime("%Y%m%d")
                url = (
                    f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/"
                    f"scoreboard?dates={date_str}"
                )
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    for evt in resp.json().get("events", []):
                        comp = evt["competitions"][0]
                        home = [t for t in comp["competitors"] if t["homeAway"] == "home"][0]
                        away = [t for t in comp["competitors"] if t["homeAway"] == "away"][0]
                        all_games.append({
                            "season": f"{season}-{season+1}",
                            "date": date_str,
                            "home_team": home["team"]["displayName"],
                            "away_team": away["team"]["displayName"],
                            "home_score": home.get("score", 0),
                            "away_score": away.get("score", 0),
                            "status": evt["status"]["type"]["description"]
                        })
                date += timedelta(days=1)

        df = pd.DataFrame(all_games)
        saved_file = os.path.join(DATA_DIR, "nba_games_5yr.csv")
        df.to_csv(saved_file, index=False)
        print(f"✅ Saved ALL {len(df)} games → {saved_file}")
        return df

    except Exception as e:
        print(f"Data collection failed: {e}")
        return pd.DataFrame()
