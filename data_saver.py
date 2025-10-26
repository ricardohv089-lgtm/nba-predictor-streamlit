import os
import requests
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def collect_season_data(seasons_back=5, progress_cb=None):
    """
    Collect all NBA games from ESPN open API for past N seasons.
    Now handles ESPN scoreboard endpoint's daily cap using &limit=200&groups=50.
    Shows progress with optional callback (for Streamlit progress bar).
    """
    all_games = []
    today = datetime.today()
    start_year = today.year - seasons_back
    seasons_collected = 0
    total_seasons = (today.year + 1) - start_year

    try:
        for season in range(start_year, today.year + 1):
            print(f"Fetching season {season}-{season+1} ...")
            start = datetime(season, 10, 1)
            end = datetime(season + 1, 7, 1)
            date = start
            games_this_season = 0

            while date <= end:
                date_str = date.strftime("%Y%m%d")
                url = (
                    f"https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/"
                    f"scoreboard?dates={date_str}&limit=200&groups=50"
                )
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    games_today = 0
                    for evt in resp.json().get("events", []):
                        try:
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
                            games_today += 1
                        except Exception:
                            continue
                    games_this_season += games_today
                else:
                    print(f"⚠️ Skipped {date_str} — HTTP {resp.status_code}")

                date += timedelta(days=1)

            print(f"Season {season}-{season+1} collected {games_this_season} games.")
            seasons_collected += 1
            if progress_cb:
                progress_cb(seasons_collected / total_seasons)

        df = pd.DataFrame(all_games)
        # ESPN can sometimes duplicate game ids for playback; ensure no duplicates
        df.drop_duplicates(subset=["date", "home_team", "away_team"], inplace=True)
        saved_file = os.path.join(DATA_DIR, "nba_games_5yr.csv")
        df.to_csv(saved_file, index=False)
        print(f"✅ Saved ALL {len(df)} games → {saved_file}")
        return df

    except Exception as e:
        print(f"Data collection failed: {e}")
        return pd.DataFrame()
