# Music Recommendation System

This project builds a music recommendation system using Neo4j. It includes:

- **Data generation:** Synthetic music sessions (`generate_music.py`)
- **Data preparation:** Clean, sort, and subset data (`prep_data.py`)
- **Neo4j ingestion:** Load sessions, events, and categories into Neo4j (`load_schema.py`)
- **Co-occurrence computation:** Build CONNECTED_TO relationships (`compute_co.py`)
- **Evaluation:** Calculate MRR for the play-only test set (`eval.py`)

