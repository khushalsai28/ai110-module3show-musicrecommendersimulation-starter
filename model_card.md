# VibeMatch Model Card

## System Overview

VibeMatch is a local, retrieval-grounded music recommendation demo built on the Modules 1-3 Music Recommender Simulation. It parses supported preferences from a natural-language request, scores the fictional song catalog with an explainable content-based rule, and forms its response from the retrieved songs. It does not use a trained language model, external service, or personal listening history.

## Intended Use

Use this project to demonstrate how query interpretation, retrieval, ranking, and explanations can work together. It is intended for classroom learning and portfolio demonstration, not production recommendations, mental-health advice, or claims about commercial streaming algorithms.

## Data and Method

The local CSV contains 16 fictional songs with genre, mood, energy, tempo, valence, danceability, and acousticness features. Recommendations use genre (+2), mood (+1), energy similarity (0-1), and optional acoustic preference (up to +0.5). The parser recognizes genre and mood labels in the catalog, a small set of energy words or an explicit energy value from 0 to 1, and acoustic/unplugged preference. The answer names a song and attributes only after retrieval from the CSV.

## Limitations and Biases

- The catalog is fictional, small, and unevenly distributed across genres and moods; unsupported labels cannot be recommended.
- Fixed scoring weights reflect design choices. A +2 genre match can outweigh a mood mismatch, and one profile may not capture a listener's intent.
- Energy words are mapped to fixed values, so "chill" or "energetic" may mean something different to an individual.
- There is no artist/genre diversity constraint, no feedback loop, and no ground-truth preference data. Passing tests does not establish real-world relevance or fairness.
- The parser is rule-based and English-only; it can miss synonyms, phrasing, sarcasm, or requests with conflicting cues.

## Misuse and Mitigations

The main foreseeable misuse is presenting this small simulation as a validated production recommender or claiming that its rankings reflect real users. The README and UI disclose that the catalog is fictional and the rules are fixed. Recommendation queries are processed against the local catalog without an external model API; Streamlit usage statistics are disabled in the checked-in configuration. Unknown requests and invalid energy values are rejected rather than being represented as confident recommendations.

## Reliability and Evaluation

Automated tests cover scoring behavior, explanations, query-to-profile parsing, catalog-grounded results, and errors for empty, unsupported, or invalid requests. The project test run passed **13 tests**. Representative end-to-end CLI outputs and a structured human spot-check table are in the README. Human review confirmed that displayed song details and score reasons matched the local CSV and rule outputs; it did not measure listener satisfaction.

### What Surprised Me During Testing

The system can produce a plausible-looking ranked list even when the profile conflicts: independent genre, mood, and energy points can let one feature dominate. I also saw that a natural-language request only changes behavior when its cues are successfully mapped; a fluent or detailed request that uses an unsupported mood can be rejected rather than interpreted as intended. This reinforced the value of showing detected preferences and point-by-point reasons.

## Responsible-AI Reflection

### How I Collaborated with AI

I used an AI coding assistant to help integrate the query workflow into the recommender, add tests and a local interface, and organize reproducible documentation. I reviewed the code, ran the tests and sample commands, and checked that examples came from the CSV and matched the implemented scoring rule. The AI did not choose or validate real listener preferences; the data is fictional.

### Suggestion I Accepted

I accepted the suggestion to retrieve and score actual catalog records before composing the response, and to include the retrieved records' reasons in the output. This makes the query meaningfully affect the recommendation and keeps the answer grounded in the data rather than appending unrelated catalog facts.

### Suggestion I Rejected or Revised

The AI suggested a natural-language request experience. I revised the scope rather than claim general language understanding: the parser recognizes the catalog's own genre and mood labels plus a short list of energy and acoustic cues, and it rejects unsupported requests. I also kept response generation deterministic instead of adding a generative API, which would add setup, network, privacy, and reproducibility costs without improving this small-catalog demo.

### Remaining Risks

The transparent reasons may make the ranking understandable, but they do not prove that the weights are good or unbiased. The parser's vocabulary can privilege familiar English descriptions and the genres included in this catalog. Before any real deployment, the data would need appropriate sourcing and broader representation, the parser would need human review, and ranking quality would need evaluation with consented listener feedback and diversity checks.

## Reflection

This project taught me that retrieval, validation, and evaluation are part of an AI feature—not merely setup around it. Deterministic output made it easier to trace errors and reproduce examples, but also exposed how narrow feature rules can miss user intent. A larger dataset and carefully collected, consented feedback would be necessary before making claims about recommendation quality.
