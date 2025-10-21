from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
password = os.getenv('PASSWORD')
uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=("neo4j", password))

# Load your CSV files
df = pd.read_csv('data/music_subset.csv')
session_df = pd.read_csv('data/session_starts.csv')
cat_df = pd.read_csv('data/categories_music.csv')

def to_iso_format(dt_str):
    """Convert timestamps like '2019-10-11 18:25:00' → '2019-10-11T18:25:00'"""
    if pd.isna(dt_str):
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").isoformat()
    except ValueError:
        # If format already valid or slightly different
        return str(dt_str).replace(" ", "T")

def load_to_schema(tx, row, session_row, cat_row):
    tx.run("""
        MERGE (s:Session {sid: $sid})
        SET s.start_time = datetime($start_time),
            s.duration = $duration

        MERGE (e:Event {eid: $eid})
        SET e.name = $name,
            e.type = $type,
            e.timestamp = datetime($timestamp)

        MERGE (c:Category {catid: $catid})
        SET c.name = $cat_name,
            c.level = $level

        MERGE (e)-[:OCCURRED_IN {step: $step, action_type: $type}]->(s)
        MERGE (e)-[:BELONGS_TO]->(c)
    """,
    sid=row['Session_id'],
    start_time=to_iso_format(session_row['start_time']),
    duration=session_row['duration'],
    eid=f"{row['Session_id']}_{row['step']}",
    name=row['SubCategory'],
    type=row['Action'],
    timestamp=to_iso_format(row['DateTime']),
    catid=cat_row['catid'],
    cat_name=cat_row['name'],
    level=cat_row['level'],
    step=row['step'])

with driver.session() as session:
    for _, row in df.iterrows():
        session_row = session_df[session_df['Session_id'] == row['Session_id']].iloc[0]

        matching_rows = cat_df[
            (cat_df['Category'] == row['Category']) &
            (cat_df['SubCategory'] == row['SubCategory'])
        ]
        if not matching_rows.empty:
            matching_cat = matching_rows.iloc[0]
        else:
            matching_cat = cat_df.iloc[0]  # fallback if not found

        session.execute_write(load_to_schema, row, session_row, matching_cat)

print("✅ Music data successfully loaded into Neo4j!")

driver.close()
