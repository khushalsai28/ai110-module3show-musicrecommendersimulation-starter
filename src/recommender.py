import csv
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


logger = logging.getLogger(__name__)


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        preferences = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(preferences, asdict(song))[0],
            reverse=True,
        )
        return ranked[:max(k, 0)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        preferences = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(preferences, asdict(song))
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV and convert numeric features."""
    required_columns = {
        "id", "title", "artist", "genre", "mood", "energy", "tempo_bpm",
        "valence", "danceability", "acousticness",
    }
    float_columns = {
        "energy", "tempo_bpm", "valence", "danceability", "acousticness",
    }
    songs: List[Dict] = []

    with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{csv_path} is missing required columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            try:
                song = dict(row)
                song["id"] = int(row["id"])
                for column in float_columns:
                    song[column] = float(row[column])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid numeric value in {csv_path} on line {line_number}"
                ) from error
            songs.append(song)

    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against a profile and return the score with its reasons."""
    score = 0.0
    reasons: List[str] = []

    preferred_genre = user_prefs.get("genre", user_prefs.get("favorite_genre"))
    if preferred_genre is not None and song.get("genre") is not None:
        if str(song["genre"]).strip().casefold() == str(preferred_genre).strip().casefold():
            score += 2.0
            reasons.append("genre match (+2.0)")

    preferred_mood = user_prefs.get("mood", user_prefs.get("favorite_mood"))
    if preferred_mood is not None and song.get("mood") is not None:
        if str(song["mood"]).strip().casefold() == str(preferred_mood).strip().casefold():
            score += 1.0
            reasons.append("mood match (+1.0)")

    target_energy = user_prefs.get("energy", user_prefs.get("target_energy"))
    if target_energy is not None and song.get("energy") is not None:
        similarity = max(0.0, 1.0 - abs(float(target_energy) - float(song["energy"])))
        score += similarity
        reasons.append(f"energy similarity (+{similarity:.2f})")

    if "likes_acoustic" in user_prefs and song.get("acousticness") is not None:
        acousticness = float(song["acousticness"])
        acoustic_similarity = acousticness if user_prefs["likes_acoustic"] else 1.0 - acousticness
        acoustic_points = 0.5 * max(0.0, min(acoustic_similarity, 1.0))
        score += acoustic_points
        reasons.append(f"acoustic preference (+{acoustic_points:.2f})")

    if not reasons:
        reasons.append("no comparable preference features")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """Rank the catalog by weighted match score and explain each result."""
    scored_songs = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    ranked_songs = sorted(
        scored_songs,
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in ranked_songs[:max(k, 0)]
    ]


def _find_first_label(query: str, labels: List[str]) -> str | None:
    matches = []
    for label in labels:
        phrase = re.escape(label.casefold()).replace(r"\ ", r"\s+")
        match = re.search(
            rf"(?<![a-z0-9]){phrase}(?![a-z0-9])",
            query,
        )
        if match:
            matches.append((match.start(), -len(label), label))
    return min(matches)[2] if matches else None


def _extract_energy(query: str) -> float | None:
    numeric = re.search(
        r"\benergy\s*(?:of|at|=|:)?\s*(-?\d+(?:\.\d+)?)",
        query,
    )
    if numeric:
        energy = float(numeric.group(1))
        if not 0.0 <= energy <= 1.0:
            raise ValueError("Energy must be a number from 0 to 1.")
        return energy

    hints = (
        (0.25, ("low energy", "calm", "chill", "relaxed", "soft", "mellow", "wind down")),
        (0.5, ("moderate energy", "medium energy", "steady")),
        (0.85, ("high energy", "energetic", "upbeat", "intense", "workout", "dance")),
    )
    matches = []
    for energy, phrases in hints:
        for phrase in phrases:
            match = re.search(
                rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])",
                query,
            )
            if match:
                matches.append((match.start(), energy))
    return min(matches)[1] if matches else None


def profile_from_query(query: str, songs: List[Dict]) -> Dict:
    """Extract catalog labels and preference cues from a natural-language request."""
    normalized_query = " ".join(query.casefold().replace("-", " ").split())
    if not normalized_query:
        raise ValueError("Enter a music request before searching.")

    genres = sorted({str(song["genre"]) for song in songs if song.get("genre")})
    moods = sorted({str(song["mood"]) for song in songs if song.get("mood")})
    profile: Dict = {}
    genre = _find_first_label(normalized_query, genres)
    mood = _find_first_label(normalized_query, moods)
    energy = _extract_energy(normalized_query)
    if genre:
        profile["genre"] = genre
    if mood:
        profile["mood"] = mood
    if energy is not None:
        profile["energy"] = energy

    if re.search(
        r"\b(?:not|no|non|avoid|don't want|do not want)\s+acoustic\b",
        normalized_query,
    ):
        profile["likes_acoustic"] = False
    elif re.search(r"\b(?:acoustic|unplugged)\b", normalized_query):
        profile["likes_acoustic"] = True

    if not profile:
        logger.info("Query contained no recognized catalog preferences")
        raise ValueError(
            "I couldn't identify a genre, mood, energy, or acoustic preference. "
            "Try a catalog genre or mood such as 'lofi', 'chill', or 'pop'."
        )

    logger.info("Extracted music preferences: %s", profile)
    return profile


def recommend_from_query(
    query: str,
    songs: List[Dict],
    k: int = 5,
) -> Tuple[Dict, List[Tuple[Dict, float, str]], str]:
    """Retrieve and explain catalog songs using preferences found in a request."""
    if k < 1:
        raise ValueError("The number of recommendations must be at least 1.")

    profile = profile_from_query(query, songs)
    results = recommend_songs(profile, songs, k=k)
    logger.info("Retrieved %s recommendations from %s catalog songs", len(results), len(songs))

    if not results:
        return profile, results, "The song catalog is empty, so I couldn't find a recommendation."

    song, score, explanation = results[0]
    answer = (
        f"I found {len(songs)} songs in the catalog for your request. "
        f"Top pick: {song['title']} by {song['artist']} "
        f"({song['genre']}, {song['mood']}, energy {song['energy']:.2f}). "
        f"It ranked first because {explanation} (score {score:.2f})."
    )
    return profile, results, answer
