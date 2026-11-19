# VibeMatch: Retrieval-Grounded Music Recommendations

VibeMatch turns a short natural-language music request into ranked, explainable recommendations from a local song catalog. It identifies preferences the catalog can support, retrieves and scores matching songs, then builds its answer from those retrieved song records. The project is deterministic and local: it does not call an external language model or claim to model a commercial streaming service.

## Original Project

The original Modules 1-3 project was **Music Recommender Simulation**. It explored a small, fictional song catalog and ranked songs against a listener profile using genre, mood, energy, and optional acoustic preference. It was a CLI-first content-based recommendation baseline with score explanations, not a model trained on listening histories or a reproduction of Spotify or TikTok.

## How It Works

Users can try VibeMatch in a browser or from the command line. The query parser recognizes genre and mood labels present in the catalog, common energy descriptions (or a numeric target from 0 to 1), and acoustic preference. The existing transparent scorer ranks the catalog, and the response uses the retrieved top song's real title, artist, metadata, score, and match reasons. Unknown requests and invalid energy values produce an actionable error instead of an ungrounded recommendation.

This is a small **retrieval-augmented recommendation workflow**: the request is interpreted into catalog-supported preferences, the local CSV is scored and ranked, and retrieved records directly determine the answer. It is not free-form LLM generation. The dataset contains 16 fictional songs, so a recognized cue is limited to this vocabulary.

## Architecture

The source diagram is [diagrams/system_architecture.mmd](diagrams/system_architecture.mmd). A request flows through preference extraction, local CSV retrieval/ranking, then into a response composed from the selected records. Automated tests check ranking, grounding, parsing, and invalid input; a human spot-check table below records representative output review. The browser UI is `src/app.py`; the CLI and shared recommendation logic are `src/main.py` and `src/recommender.py`.

## Setup

Requires Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Run the browser app

```powershell
python -m streamlit run src/app.py --server.address 127.0.0.1 --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501). Enter a natural-language request and select how many songs to see.

### Run the CLI

```powershell
python -m src.main --query "I want chill lofi, low energy, and acoustic music" --top-k 3
```

Without `--query`, the CLI runs the original four-profile demonstration.

### Run the tests

```powershell
python -m pytest -q
```

The recommendation algorithm uses only the Python standard library. Streamlit provides the browser UI; pytest runs the automated checks.

## Reproducible Execution Evidence

The following examples were run with `python -m src.main` against `data/songs.csv` (16 songs). The CLI logs detected preferences and result counts, and each response gives the retrieved song and why it ranked first.

### Example 1: chill lofi and acoustic

**Input**

```text
I want chill lofi, low energy, and acoustic music
```

**Command and output**

```text
> python -m src.main --query "I want chill lofi, low energy, and acoustic music" --top-k 3
INFO: Extracted music preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.25, 'likes_acoustic': True}
INFO: Retrieved 3 recommendations from 16 catalog songs
Detected preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.25, 'likes_acoustic': True}
I found 16 songs in the catalog for your request. Top pick: Library Rain by Paper Lanterns (lofi, chill, energy 0.35). It ranked first because genre match (+2.0); mood match (+1.0); energy similarity (+0.90); acoustic preference (+0.43) (score 4.33).
1. Library Rain - Paper Lanterns (score 4.33)
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.90); acoustic preference (+0.43)
2. Midnight Coding - LoRoom (score 4.19)
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.83); acoustic preference (+0.35)
3. Focus Flow - LoRoom (score 3.24)
   Because: genre match (+2.0); energy similarity (+0.85); acoustic preference (+0.39)
```

### Example 2: upbeat pop with a numeric target

**Input**

```text
upbeat pop energy 0.8
```

**Command and output**

```text
> python -m src.main --query "upbeat pop energy 0.8" --top-k 3
INFO: Extracted music preferences: {'genre': 'pop', 'energy': 0.8}
INFO: Retrieved 3 recommendations from 16 catalog songs
Detected preferences: {'genre': 'pop', 'energy': 0.8}
I found 16 songs in the catalog for your request. Top pick: Sunrise City by Neon Echo (pop, happy, energy 0.82). It ranked first because genre match (+2.0); energy similarity (+0.98) (score 2.98).
1. Sunrise City - Neon Echo (score 2.98)
   Because: genre match (+2.0); energy similarity (+0.98)
2. Gym Hero - Max Pulse (score 2.87)
   Because: genre match (+2.0); energy similarity (+0.87)
3. Rooftop Lights - Indigo Parade (score 0.96)
   Because: energy similarity (+0.96)
```

### Example 3: calm classical and acoustic

**Input**

```text
calm classical, acoustic
```

**Command and output**

```text
> python -m src.main --query "calm classical, acoustic" --top-k 3
INFO: Extracted music preferences: {'genre': 'classical', 'mood': 'calm', 'energy': 0.25, 'likes_acoustic': True}
INFO: Retrieved 3 recommendations from 16 catalog songs
Detected preferences: {'genre': 'classical', 'mood': 'calm', 'energy': 0.25, 'likes_acoustic': True}
I found 16 songs in the catalog for your request. Top pick: Paper Moons by Elara Vale (classical, calm, energy 0.19). It ranked first because genre match (+2.0); mood match (+1.0); energy similarity (+0.94); acoustic preference (+0.48) (score 4.42).
1. Paper Moons - Elara Vale (score 4.42)
   Because: genre match (+2.0); mood match (+1.0); energy similarity (+0.94); acoustic preference (+0.48)
2. Spacewalk Thoughts - Orbit Bloom (score 1.43)
   Because: energy similarity (+0.97); acoustic preference (+0.46)
3. Library Rain - Paper Lanterns (score 1.33)
   Because: energy similarity (+0.90); acoustic preference (+0.43)
```

### Guardrail example

An unrecognized request is rejected rather than silently returning an arbitrary ranking:

```text
> python -m src.main --query "give me something new"
INFO: Query contained no recognized catalog preferences
ERROR: I couldn't identify a genre, mood, energy, or acoustic preference. Try a catalog genre or mood such as 'lofi', 'chill', or 'pop'.
Process exit code: 2
```

### Reliability and human review

Automated checks run via pytest; the results below record checks run in this project, not recommendation accuracy against real listener feedback.

| Check | Expected behavior | Result |
|---|---|---|
| Catalog query: chill lofi, low energy, acoustic | Top pick is a retrieved catalog song; metadata and score reasons are consistent | Pass: Library Rain, score 4.33 |
| Catalog query: upbeat pop, energy 0.8 | Pop and energy preferences affect ranking; top pick comes from catalog | Pass: Sunrise City, score 2.98 |
| Unknown query | Actionable error, no arbitrary recommendations | Pass: CLI exits with code 2 |
| Numeric energy outside 0-1 | Reject with range guidance | Pass: automated guardrail test |
| Automated test suite | Scoring, query parsing, grounding, and input guardrails pass | Pass: 13 tests |

During human spot-checking, the strongest matching records and their displayed reasons agreed with the CSV and scoring rules. This checks implementation consistency, not whether a real listener would enjoy the songs. There are no users, preference labels, or ground-truth judgments in the dataset.

## Design Decisions and Trade-offs

- **Local retrieval and deterministic output:** using the CSV avoids API keys, network access, and fabricated song details; the trade-off is limited vocabulary and no generative flexibility.
- **Existing weighted scorer:** genre, mood, energy similarity, and acoustic preference keep results explainable and make this an extension of the original project; fixed weights can still overvalue a feature.
- **Guardrails and logs:** the parser rejects empty/unsupported requests and out-of-range energy; logs record extracted preferences and retrieval counts without recording the raw request.
- **Privacy defaults:** recommendation queries stay local, and checked-in Streamlit configuration disables usage statistics.
- **Browser and CLI share logic:** both call the same recommendation function, reducing behavior drift, at the cost of a small UI dependency on Streamlit.

## What I Learned

Building a useful AI-shaped feature is not only about producing fluent text: the input interpretation and data retrieval must change which results are selected, and the answer should be traceable to those records. Tests can establish that the pipeline behaves consistently, but they cannot substitute for real listener evaluation or reveal whether the catalog itself is representative. See [model_card.md](model_card.md) for limitations, misuse considerations, and my AI-collaboration reflection.

## Portfolio

- **Code:** [khushalsai28/ai110-module3show-musicrecommendersimulation-starter](https://github.com/khushalsai28/ai110-module3show-musicrecommendersimulation-starter)
- **What this project says about me as an AI engineer:** I build systems that connect a user's request to relevant data, make their decisions inspectable, and fail clearly when the evidence is missing. I value reproducible tests and responsible limits as much as a working demo.
- **Presentation:** See the [6-minute presentation outline](presentation.md) for a timed walkthrough.
