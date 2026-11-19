"""Streamlit interface for catalog-grounded music recommendations."""

import logging
from pathlib import Path
from typing import Dict, List

import streamlit as st

from src.recommender import load_songs, recommend_from_query


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@st.cache_data
def load_catalog() -> List[Dict]:
    catalog_path = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
    return load_songs(str(catalog_path))


st.set_page_config(page_title="VibeMatch")
st.title("VibeMatch")
st.write(
    "Describe a mood, genre, or energy level. VibeMatch searches the local song "
    "catalog and explains why its top results fit."
)

with st.form("recommendation_form"):
    query = st.text_input(
        "What are you in the mood for?",
        placeholder="chill lofi, low energy, acoustic",
    )
    top_k = st.slider("Recommendations", min_value=1, max_value=10, value=5)
    submitted = st.form_submit_button("Find songs")

if submitted:
    try:
        profile, recommendations, answer = recommend_from_query(query, load_catalog(), k=top_k)
    except ValueError as error:
        logging.warning("Recommendation request was not usable: %s", error)
        st.warning(str(error))
    else:
        st.caption(f"Preferences identified: {profile}")
        st.success(answer)
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            st.subheader(f"{rank}. {song['title']} - {song['artist']}")
            st.write(
                f"**{song['genre']} / {song['mood']}** | "
                f"Energy {song['energy']:.2f} | Match score {score:.2f}"
            )
            st.caption(f"Why it matched: {explanation}")

st.divider()
st.caption(
    "This demo uses a small fictional catalog and transparent matching rules. "
    "It does not call an external AI service or represent a listener's real preferences."
)
