import os
import pandas as pd
import numpy as np

def build_features(input_csv="data/nba_games_5yr.csv", output_csv="data/features_ready.csv"):
    """
    Create model-ready features from multi-season game data.
    Generates rolling stats, opponent differentials, and context flags.
    Output: features_ready.csv
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"{input_csv} not found.")

    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["home_score", "away_score"]).reset_index(drop=True)
    df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
    team_stats = []

    for team in pd.unique(df[["home_team", "away_team"]].values.ravel()):
        team_games = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
        team_games = team_games.sort_values("date")
        team_games["points_for"] = np.where(team_games["home_team"] == team,
                                            team_games["home_score"], team_games["away_score"])
        team_games["points_against"] = np.where(team_games["home_team"] == team,
                                                team_games["away_score"], team_games["home_score"])
        team_games["win_flag"] = (team_games["points_for"] > team_games["points_against"]).astype(int)

        for n in [5, 10]:
            team_games[f"avg_pts_{n}"] = team_games["points_for"].rolling(n, min_periods=1).mean().shift(1)
            team_games[f"avg_pa_{n}"] = team_games["points_against"].rolling(n, min_periods=1).mean().shift(1)
            team_games[f"win_rate_{n}"] = team_games["win_flag"].rolling(n, min_periods=1).mean().shift(1)

        team_games["is_home"] = (team_games["home_team"] == team).astype(int)
        team_games["team_name"] = team
        team_stats.append(team_games)

    combined = pd.concat(team_stats).sort_values("date").reset_index(drop=True)
    combined = combined.dropna().reset_index(drop=True)

    feature_cols = [
        "date", "team_name", "is_home", "avg_pts_5", "avg_pa_5", "win_rate_5",
        "avg_pts_10", "avg_pa_10", "win_rate_10", "points_for", "points_against", "win_flag"
    ]
    feats = combined[feature_cols].copy().dropna()
    feats.to_csv(output_csv, index=False)
    print(f"✅ Features ready: {output_csv} - {len(feats)} rows.")
    return feats

# (rest of your code as before)
