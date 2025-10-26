import os, joblib, pandas as pd, numpy as np
import xgboost as xgb

MODELS_DIR = "models"
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

def load_models():
    """Load saved base and meta models."""
    models = {}
    for name in ["xgb", "rf", "lr", "meta_stacker"]:
        path = os.path.join(MODELS_DIR, f"{name}.pkl")
        if os.path.exists(path):
            models[name] = joblib.load(path)
        else:
            raise FileNotFoundError(f"Model {path} not found.")
    scaler = joblib.load(SCALER_PATH)
    return models, scaler


def prepare_features_for_prediction(live_games_df):
    """
    Dummy feature generator until live rolling stats exist.
    For demo purposes, fill statistical averages based on prior model training scale.
    Expects columns: home_team, away_team.
    """
    base = []
    for _, row in live_games_df.iterrows():
        base.append({
            "is_home": 1,
            "avg_pts_5": 110,
            "avg_pa_5": 108,
            "win_rate_5": 0.55,
            "avg_pts_10": 111,
            "avg_pa_10": 109,
            "win_rate_10": 0.54
        })
    return pd.DataFrame(base)


def predict_today(live_games_df):
    """
    Combine base learners and meta‑learner to predict home win probability
    for each live/upcoming game in today's ESPN scoreboard.
    """
    models, scaler = load_models()
    if live_games_df.empty:
        print("No live or upcoming games to predict.")
        return pd.DataFrame()

    # placeholder example features
    feats = prepare_features_for_prediction(live_games_df)
    X = scaler.transform(feats)

    # Get base model probabilities
    meta_inputs = np.column_stack([
        models["xgb"].predict_proba(X)[:, 1],
        models["rf"].predict_proba(X)[:, 1],
        models["lr"].predict_proba(X)[:, 1]
    ])

    # Meta‑learner final prediction
    final_probs = models["meta_stacker"].predict_proba(meta_inputs)[:, 1]
    preds = np.where(final_probs > 0.5, "HOME", "AWAY")
    conf = np.round(np.abs(final_probs - 0.5) * 200, 1)  # convert to simple % confidence

    live_games_df["predicted_winner"] = preds
    live_games_df["home_win_prob"] = np.round(final_probs * 100, 2)
    live_games_df["confidence_%"] = conf
    return live_games_df[["home_team", "away_team", "predicted_winner", "home_win_prob", "confidence_%"]]
