# Music Recommendation System

This project builds a music recommendation system using Neo4j. It includes:

- **Data generation:** Synthetic music sessions (`generate_music.py`)
- **Data preparation:** Clean, sort, and subset data (`prep_data.py`)
- **Neo4j ingestion:** Load sessions, events, and categories into Neo4j (`load_schema.py`)
- **Co-occurrence computation:** Build CONNECTED_TO relationships (`compute_co.py`)
- **Evaluation:** Calculate MRR for the play-only test set (`eval.py`)

## Usage

1. Prepare environment variables in `.env` (Neo4j URI, password).
2. Generate or load dataset (`generate_music.py` or `music_subset.xlsx`).
3. Run `prep_data.py` to clean and subset data.
4. Load schema into Neo4j with `load_schema.py`.
5. Compute co-occurrence edges using `compute_co.py`.
6. Evaluate recommendations with `eval.py`.

## Notes

- The dataset is synthetic; perfect MRR is expected for small sets.
- Only 'play' actions are considered for evaluation.
