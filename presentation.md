# VibeMatch Presentation Outline (6 Minutes)

## Slide 1 - Project and Original Goal (0:45)

**Show:** VibeMatch title and the project repository.

**Say:** The original Modules 1-3 Music Recommender Simulation ranked a small fictional song catalog from genre, mood, energy, and optional acoustic preferences. I extended that baseline so someone can describe what they want in ordinary language and receive explainable results.

## Slide 2 - System Architecture (1:00)

**Show:** [diagrams/system_architecture.mmd](diagrams/system_architecture.mmd).

**Say:** A request enters through the Streamlit page or CLI. The parser extracts only preferences supported by the catalog, the scorer ranks local CSV records, and the response uses retrieved song details and score reasons. Unsupported requests and invalid energy values produce an error. Tests and a human spot-check verify the outputs.

## Slide 3 - Live Demo (1:30)

**Show:** Open `http://localhost:8501` and submit: `I want chill lofi, low energy, and acoustic music`.

**Say:** The interface identifies lofi, chill, low energy, and acoustic preference. It retrieves Library Rain first and explains the genre, mood, energy, and acoustic contributions. Then try `upbeat pop energy 0.8`; Sunrise City ranks first. Both answers are built from the CSV rather than invented song information.

## Slide 4 - Reliability and Guardrails (1:00)

**Show:** Run `python -m pytest -q`, then try an unsupported CLI request.

**Say:** The 13 automated tests cover scoring, parsing, grounded results, and errors. The unsupported request exits with a clear message instead of returning an unrelated ranking. These checks show that the implementation follows its rules; they do not prove that listeners will like its recommendations.

## Slide 5 - Design and Responsible AI (1:00)

**Show:** README sample output and the `model_card.md` limitations section.

**Say:** I kept retrieval and response generation deterministic and local to avoid API setup and ungrounded song details. The trade-off is a narrow, English-only vocabulary and fixed weights. The 16 fictional songs are unevenly distributed, and a genre score can outweigh a mood mismatch. This is a classroom demo, not a production recommender.

## Slide 6 - What I Learned and Next Steps (0:45)

**Show:** README testing table and portfolio reflection.

**Say:** I learned that a useful AI workflow depends on reliable input interpretation and evidence-grounded output, not just fluent responses. Tests can catch behavior regressions but cannot evaluate taste or fairness. My next step would be a larger, responsibly sourced catalog and consented listener feedback before making quality claims.
