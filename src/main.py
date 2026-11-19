"""
Command line runner for the Music Recommender Simulation.

Run a natural-language request or the built-in profile demonstration.
"""

import argparse
import logging
from pathlib import Path

from .recommender import load_songs, recommend_from_query, recommend_songs


logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Get explainable music recommendations.")
    parser.add_argument(
        "--query",
        help="Describe the music you want, for example: 'chill lofi, low energy, acoustic'.",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of songs to recommend.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    catalog_path = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
    songs = load_songs(str(catalog_path))
    if args.query is not None:
        try:
            profile, results, answer = recommend_from_query(args.query, songs, k=args.top_k)
        except ValueError as error:
            logger.error("%s", error)
            raise SystemExit(2) from error

        print(f"Detected preferences: {profile}")
        print(answer)
        for rank, (song, score, explanation) in enumerate(results, start=1):
            print(f"{rank}. {song['title']} - {song['artist']} (score {score:.2f})")
            print(f"   Because: {explanation}")
        return

    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8}),
        ("Chill Acoustic", {
            "genre": "lofi", "mood": "chill", "energy": 0.35,
            "likes_acoustic": True,
        }),
        ("Intense Rock", {"genre": "metal", "mood": "intense", "energy": 0.9}),
        ("Conflicting Preferences", {
            "genre": "metal", "mood": "calm", "energy": 0.95,
        }),
    ]

    print(f"Loaded songs: {len(songs)}")
    for profile_name, user_prefs in profiles:
        print(f"\n{profile_name} profile: {user_prefs}")
        for rank, (song, score, explanation) in enumerate(
            recommend_songs(user_prefs, songs, k=5),
            start=1,
        ):
            print(f"{rank}. {song['title']} - {score:.2f}")
            print(f"   Because: {explanation}")


if __name__ == "__main__":
    main()
