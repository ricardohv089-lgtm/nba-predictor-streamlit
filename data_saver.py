import os, requests, pandas as pd
from datetime import datetime, timedelta

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def collect_season_data(seasons_back=5):
    """
    Collect all NBA games from ESPN open API for past N seasons.
    Each ESPN season spans Oct–Jun. Saves results as CSV per season.
    """
    try:
        today = datetime.today()
        start_year = today.year - seasons_back
        all_games = []

        for season in range(start_year, today.year + 1):
            # Pull every day between Oct 1 and July 1
            start = datetime(season, 10, 1)
            end = datetime(season + 1, 7, 1)
            current = start
            print(f"Fetching season {season}-{season+1}")
            while current <= end:
                date_str = current.strftime("%Y%m%d")
                url = f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_str}"
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
                current += timedelta(days=1)

        df = pd.DataFrame(all_games)
        out_path = os.path.join(DATA_DIR, "nba_games_5yr.csv")
        df.to_csv(out_path, index=False)
        print(f"✅ Data saved to {out_path}, total games: {len(df)}")
        return df
    except Exception as e:
        print("Collect error:", e)
        return pd.DataFrame()
