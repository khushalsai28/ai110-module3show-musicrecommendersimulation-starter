from pathlib import Path

import pytest

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_rewards_matches_and_nearby_energy():
    score, reasons = score_song(
        {"genre": "POP", "mood": "happy", "energy": 0.7},
        {"genre": "pop", "mood": "happy", "energy": 0.8},
    )

    assert score == 3.9
    assert reasons == [
        "genre match (+2.0)",
        "mood match (+1.0)",
        "energy similarity (+0.90)",
    ]


def test_score_song_uses_acousticness_only_when_requested():
    song = {"acousticness": 0.8}

    liked_score, liked_reasons = score_song({"likes_acoustic": True}, song)
    disliked_score, _ = score_song({"likes_acoustic": False}, song)

    assert liked_score == 0.4
    assert liked_reasons == ["acoustic preference (+0.40)"]
    assert disliked_score == pytest.approx(0.1)


def test_recommend_songs_ranks_without_mutating_catalog():
    songs = [
        {"title": "Chill", "genre": "lofi", "mood": "chill", "energy": 0.4},
        {"title": "Pop", "genre": "pop", "mood": "happy", "energy": 0.8},
    ]

    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
        k=1,
    )

    assert [result[0]["title"] for result in results] == ["Pop"]
    assert results[0][1] == 4.0
    assert "genre match (+2.0)" in results[0][2]
    assert [song["title"] for song in songs] == ["Chill", "Pop"]


def test_load_songs_converts_csv_numeric_fields():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
    songs = load_songs(str(csv_path))

    assert len(songs) == 16
    assert songs[0]["id"] == 1
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], float)


def test_recommender_returns_empty_list_for_nonpositive_k():
    assert recommend_songs({}, [{"title": "Only song"}], k=0) == []
