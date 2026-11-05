"""
Command line runner for the Music Recommender Simulation.

Run the recommender with several sample taste profiles.
"""

from pathlib import Path

from .recommender import load_songs, recommend_songs

def main() -> None:
    catalog_path = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
    songs = load_songs(str(catalog_path))
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
