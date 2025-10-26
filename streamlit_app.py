import os
import sys
import streamlit as st
import pandas as pd

import data_fetcher as df
from data_saver import collect_season_data
import model_predictor as mp
import model_trainer as trainer

# Ensure local imports
sys.path.append(os.path.dirname(__file__))

st.set_page_config(page_title="🏀 NBA Prediction System", layout="wide")

st.title("🏀 NBA Prediction System — Real Data + Machine Learning Forecasts")
st.markdown("""
Fetch live NBA data, build a multi‑season dataset, and forecast Moneyline outcomes
using a **stacked ensemble (XGBoost + Random Forest + Logistic Regression)**.
""")

# -------------------------------
# 1. LIVE / UPCOMING GAMES
# -------------------------------
st.subheader("🏟️ Live / Upcoming Games (ESPN Feed)")
live_games = df.get_live_scoreboard()
if live_games.empty:
    st.info("No live or upcoming NBA games right now.")
else:
    st.dataframe(live_games, use_container_width=True)

# -------------------------------
# 2. HISTORICAL SCORES
# -------------------------------
st.subheader("📚 Past Week Final Scores (ESPN)")
past_games = df.get_historical_games()
if past_games.empty:
    st.info("No final score data available right now.")
else:
    st.dataframe(past_games, use_container_width=True)

# -------------------------------
# 3. DATASET COLLECTION
# -------------------------------
st.subheader("🗂️ Collect and Save Full Dataset (3‑5 Seasons)")
seasons_back = st.slider("How many seasons to collect ?", 3, 5, 5)

if st.button("Collect Dataset"):
    progress_bar = st.progress(0.0)
    def prog_cb(frac):
        progress_bar.progress(frac)
    with st.spinner("Collecting multi‑season data..."):
        dataset = collect_season_data(seasons_back, progress_cb=prog_cb)
    progress_bar.empty()
    if not dataset.empty:
        st.success(f"Data saved — {len(dataset)} games ✅")
        st.dataframe(dataset, use_container_width=True)
        csv_bytes = dataset.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Full Dataset (CSV)",
            csv_bytes,
            file_name="nba_games_5yr.csv",
            mime="text/csv"
        )
    else:
        st.error("Collection failed — check network or ESPN availability.")

# -------------------------------
# 4. TRAIN / RETRAIN MODELS
# -------------------------------
st.subheader("⚙️ Training / Retraining the Stacked Ensemble Model")
if st.button("Retrain Models"):
    with st.spinner("Training ensemble (XGB + RF + LR + Meta XGB)... ⏳"):
        acc, auc, f1 = trainer.train_stacked_model()
    st.success(f"Models trained and saved ✅ ACC:{acc:.2f} AUC:{auc:.2f} F1:{f1:.2f}")

# -------------------------------
# 5. PREDICTIONS
# -------------------------------
st.subheader("🤖 Predictions — Today’s Games (Moneyline Forecast)")
try:
    if live_games.empty:
        st.info("No games available for prediction right now.")
    else:
        preds = mp.predict_today(live_games)
        if preds.empty:
            st.warning("Prediction skipped — models might be missing. Train first above 👆")
        else:
            st.dataframe(preds, use_container_width=True)
            st.success("Predictions generated ✅")
except Exception as e:
    st.error(f"Prediction error: {e}")

st.caption("Data from ESPN public feeds | Models trained with real multi-season NBA data.")
