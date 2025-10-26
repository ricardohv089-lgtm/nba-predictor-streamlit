import os, sys, streamlit as st, pandas as pd
import data_fetcher as df
from data_saver import collect_season_data
import model_predictor as mp

# Ensure local modules resolve both locally and on Streamlit Cloud
sys.path.append(os.path.dirname(__file__))

st.set_page_config(page_title="🏀 NBA Prediction System — Full ML Dashboard", layout="wide")

st.title("🏀 NBA Prediction System — Real Public Data + Machine Learning Forecasts")
st.markdown("""
This app collects real **NBA data** from [ESPN public JSON feeds](https://site.web.api.espn.com)
and applies a **stacked ensemble machine learning model** (XGBoost + Random Forest + Logistic Regression meta‑learner)
to predict Moneyline outcomes.
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
    st.warning("Collecting multiple seasons... may take several minutes ⏳")
    dataset = collect_season_data(seasons_back)
    if not dataset.empty:
        st.success(f"Data saved — {len(dataset)} games total ✅")
        st.dataframe(dataset.head(20))
    else:
        st.error("Collection failed. Check network availability or ESPN rate limit.")

# -------------------------------
# 4. MACHINE LEARNING PREDICTIONS
# -------------------------------
st.subheader("🤖 Predictions — Today’s Games (Moneyline Forecast)")

try:
    if live_games.empty:
        st.info("No live games to predict right now.")
    else:
        prediction_table = mp.predict_today(live_games)
        if prediction_table.empty:
            st.info("Prediction features unavailable (check model files).")
        else:
            st.dataframe(prediction_table, use_container_width=True)
            st.success("Predictions generated ✅")
except Exception as e:
    st.error(f"Prediction error: {e}")

# -------------------------------
# FOOTER
# -------------------------------
st.caption("All data from ESPN public feeds. Models trained locally on five seasons of real NBA data.")
