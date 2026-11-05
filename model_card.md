# Model Card: VibeMatch 1.0

## 1. Model Name

**VibeMatch 1.0** - an explainable, content-based music recommender simulation.

## 2. Intended Use

VibeMatch is for classroom exploration of how song features and a taste profile can become ranked suggestions. It assumes that a listener can express preferences as a genre, mood, target energy, and optional acoustic preference. It is not intended for real users, commercial ranking, or claims about how Spotify, TikTok, or another platform works internally.

## 3. How the Model Works

The model compares each song with one profile. A matching genre adds 2 points, a matching mood adds 1 point, and energy adds a similarity score from 0 to 1 based on the distance between the song and target energy. If the profile states an acoustic preference, acousticness contributes up to 0.5 points. It then sorts all songs by score and returns the highest-ranked K, with reasons for the points. The scoring rule evaluates one song; the ranking rule orders the catalog by those scores.

## 4. Data

The dataset has 16 fictional songs with genre, mood, energy, tempo, valence, danceability, and acousticness features. The score currently uses only genre, mood, energy, and optional acousticness. There are 13 genre labels and 11 mood labels, with some labels represented by only one song. The catalog does not include real listening behavior, playlists, skips, likes, popularity, lyrics, or demographic data.

## 5. Strengths

- The same scoring logic handles different profiles, and its point contributions are easy to inspect.
- The high-energy pop profile ranks Sunrise City first; the chill acoustic profile ranks Library Rain first; the intense metal profile ranks Iron Skyline first.
- The explanation shows why a song received points, making the result easier to discuss than a ranking with no stated rationale.

## 6. Limitations and Bias

The small, uneven dataset can bias results toward the genres and moods that happen to be present, and the +2 genre weight can dominate a preference mismatch. For example, the conflicting metal/calm/high-energy profile ranks Iron Skyline first because it matches genre and energy, even though its mood is intense rather than calm. The system also lacks a diversity penalty, so repeated artists or genres can cluster in the recommendations. It has no listening outcomes or ground truth labels, so plausible-looking results do not demonstrate that a listener will like them.

## 7. Evaluation

Four profiles were run: high-energy pop, chill acoustic, intense metal, and a conflicting metal/calm/high-energy profile. The pop profile favored Sunrise City and Gym Hero, while the chill profile shifted toward Library Rain, Midnight Coding, and Focus Flow; this matches their genre, mood, energy, and acoustic features. The intense metal profile put Iron Skyline first, while the conflicting profile still ranked Iron Skyline first because the genre match and near-target energy outweighed its mood mismatch. In a separate weight-shift experiment, halving genre weight and doubling energy weight kept the same top five pop songs but moved Rooftop Lights above Gym Hero. Tests also verify scoring reasons, sorted output, numeric CSV values, and behavior for K=0. This is a behavior check against expected rules, not a measured evaluation against ground truth listener choices.

## 8. Future Work

- Add more balanced, licensed or carefully curated songs and capture explicit user feedback.
- Use playlist, like, and skip signals to compare content-based rankings with collaborative filtering.
- Add diversity controls and test ranking quality with judged relevance or offline metrics.

## 9. Personal Reflection

This project illustrates how a small model can feel personalized even though it only combines a few features and fixed weights. Its explanations make the scoring transparent, while the conflicting-profile example shows that a high score can still miss a listener's intent. AI assistance can help implement and explain the design, but the dataset, formulas, sample outputs, and tests still need independent checking. A useful next step would be testing a larger, more balanced catalog with actual listener feedback.
