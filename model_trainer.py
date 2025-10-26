import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from sklearn.preprocessing import StandardScaler

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

def train_stacked_model(input_csv="data/features_ready.csv", models_dir="models"):
    """
    Train stacked ensemble (XGBoost + RF + Logistic -> meta-XGBoost)
    for Moneyline (win/loss) prediction.
    Saves final model files under /models.
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"{input_csv} not found.")
    os.makedirs(models_dir, exist_ok=True)

    df = pd.read_csv(input_csv)
    X = df[["is_home", "avg_pts_5", "avg_pa_5", "win_rate_5",
            "avg_pts_10", "avg_pa_10", "win_rate_10"]].values
    y = df["win_flag"].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # chronological split
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                       test_size=0.15,
                                                       shuffle=False)

    # Base models
    model_xgb = xgb.XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=5,
        subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
        random_state=42, n_jobs=-1
    )
    model_rf = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42, n_jobs=-1
    )
    model_lr = LogisticRegression(max_iter=1000, solver="liblinear")

    base_models = [("xgb", model_xgb), ("rf", model_rf), ("lr", model_lr)]

    # Out-of-fold meta features
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    meta_features = np.zeros((X_train.shape[0], len(base_models)))
    test_meta = np.zeros((X_test.shape[0], len(base_models)))

    for idx, (name, model) in enumerate(base_models):
        print(f"Training base model: {name}")
        oof_preds = np.zeros(X_train.shape[0])
        for fold, (train_idx, val_idx) in enumerate(kf.split(X_train, y_train)):
            model.fit(X_train[train_idx], y_train[train_idx])
            oof_preds[val_idx] = model.predict_proba(X_train[val_idx])[:, 1]
        meta_features[:, idx] = oof_preds
        test_meta[:, idx] = model.predict_proba(X_test)[:, 1]
        joblib.dump(model, os.path.join(models_dir, f"{name}.pkl"))

    # Meta learner (XGBoost)
    meta_model = xgb.XGBClassifier(
        n_estimators=250, learning_rate=0.1, max_depth=3,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        eval_metric="logloss"
    )
    print("Training meta-learner...")
    meta_model.fit(meta_features, y_train)
    final_preds = meta_model.predict(test_meta)
    acc = accuracy_score(y_test, final_preds)
    auc = roc_auc_score(y_test, final_preds)
    f1 = f1_score(y_test, final_preds)

    print(f"✅ Stacked Model Results → ACC:{acc:.3f}  AUC:{auc:.3f}  F1:{f1:.3f}")
    joblib.dump(meta_model, os.path.join(models_dir, "meta_stacker.pkl"))
    joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
    print(f"Models saved in {models_dir}.")
    return acc, auc, f1
