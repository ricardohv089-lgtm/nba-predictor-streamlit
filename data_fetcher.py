import requests
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd

# Fetch recent games for a team from NBA.com data
def get_team_recent_games(team_id='1610612738', season='2024-25'):
    games = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=team_id,
        season_nullable=season
    ).get_data_frames()[0]
    return games

# Fetch live odds (moneyline, spread, totals) from The Odds API
def get_live_odds():
    api_key = "YOUR_API_KEY"  # Replace with your Odds API key
    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        'api_key': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.text)
        return []
