import os, joblib, pandas as pd, numpy as np
import xgboost as xgb

MODELS_DIR = "models"
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

def load_models():
    """Load base and meta ensemble models."""
    required = ["xgb", "rf", "lr", "meta_stacker"]
    models = {}
    for name in required:
        path = os.path.join(MODELS_DIR, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing model: {path}")
        models[name] = joblib.load(path)
    scaler = joblib.load(SCALER_PATH)
    return models, scaler


def prepare_features_for_prediction(live_df):
    """
    Temporary feature generator for live games until
    rolling stats integration (Phase V).
    """
    placeholder = []
    for _, _ in live_df.iterrows():
        placeholder.append({
            "is_home": 1,
            "avg_pts_5": 111, "avg_pa_5": 108, "win_rate_5": 0.55,
            "avg_pts_10": 112, "avg_pa_10": 109, "win_rate_10": 0.56
        })
    return pd.DataFrame(placeholder)


def predict_today(live_df):
    """Predict Moneyline outcomes for today's games."""
    models, scaler = load_models()
    if live_df.empty:
        return pd.DataFrame()

    feats = prepare_features_for_prediction(live_df)
    X = scaler.transform(feats)

    # Level‑0 predictions
    meta_inputs = np.column_stack([
        models["xgb"].predict_proba(X)[:, 1],
        models["rf"].predict_proba(X)[:, 1],
        models["lr"].predict_proba(X)[:, 1]
    ])

    # Meta learner output
    final_probs = models["meta_stacker"].predict_proba(meta_inputs)[:, 1]
    predicted = np.where(final_probs > 0.5, "HOME", "AWAY")
    conf = np.round(np.abs(final_probs - 0.5) * 200, 1)

    live_df["predicted_winner"] = predicted
    live_df["home_win_prob_%"] = np.round(final_probs * 100, 2)
    live_df["confidence_%"] = conf
    return live_df[["home_team", "away_team", "predicted_winner", "home_win_prob_%", "confidence_%"]]
