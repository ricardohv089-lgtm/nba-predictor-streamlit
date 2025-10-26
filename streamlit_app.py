import os, sys, streamlit as st, pandas as pd
import data_fetcher as df
from data_saver import collect_season_data

sys.path.append(os.path.dirname(__file__))

st.set_page_config(page_title="🏀 NBA Dataset Collector", layout="wide")
st.title("🏀 NBA Data Collector & Real‑Time Dashboard (ESPN Open Feeds)")

st.markdown("""
Collect multi‑season NBA game data and analyze live results.  
No API‑keys required; data fetched directly from ESPN public endpoints.
""")

# -------------------------------
# LIVE GAMES SECTION
# -------------------------------
st.subheader("🏟️ Live / Upcoming Games ")
live = df.get_live_scoreboard()
st.dataframe(live if not live.empty else pd.DataFrame([{"Info": "No live games right now"}]), use_container_width=True)

# -------------------------------
# HISTORICAL PAST WEEK SECTION
# -------------------------------
st.subheader("📚 Past Week Final Scores")
week = df.get_historical_games()
st.dataframe(week if not week.empty else pd.DataFrame([{"Info": "No recent finals"}]), use_container_width=True)

# -------------------------------
# DATA COLLECTION SECTION
# -------------------------------
st.subheader("🗂️ Collect and Save Full Dataset (3‑5 Seasons)")
seasons_back = st.slider("How many seasons to collect ?", 3, 5, 5)
if st.button("Collect Dataset"):
    st.info(f"Collecting past {seasons_back} seasons — please wait a few minutes ⏳")
    dataset = collect_season_data(seasons_back)
    if not dataset.empty:
        st.success(f"Saved {len(dataset)} games from {seasons_back} seasons ✅")
        st.dataframe(dataset.head(25))
    else:
        st.error("Failed to collect data — check connection or ESPN availability.")

st.caption("All data imported from ESPN open JSON feeds (official public source).")
