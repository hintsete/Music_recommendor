from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv('PASSWORD')

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    auth=("neo4j", password)
)

# df = pd.read_csv('data/music_subset.csv')
df = pd.read_csv('data/train_music.csv')

total_sessions = df['Session_id'].nunique()

def calc_coocc(tx, total_sessions):
    tx.run("""
        MATCH (s:Session)<-[:OCCURRED_IN]-(e1:Event), (s)<-[:OCCURRED_IN]-(e2:Event)
        WHERE e1.eid < e2.eid AND e1.type = 'play' AND e2.type = 'play'
        WITH e1, e2, datetime(e1.timestamp) AS t1, datetime(e2.timestamp) AS t2, s
        WITH e1, e2, s, abs(duration.inSeconds(t1, t2).seconds) AS time_diff
        MERGE (e1)-[r:CONNECTED_TO]->(e2)
        ON CREATE SET r.popularity = 1,
                      r.decay = exp(-time_diff / 86400.0),   // 1-day decay factor
                      r.weight = r.decay / $total_sessions
        ON MATCH SET r.popularity = r.popularity + 1,
                     r.decay = exp(-time_diff / 86400.0),
                     r.weight = r.weight + (r.decay / $total_sessions)
    """, total_sessions=total_sessions)


with driver.session() as session:
    session.execute_write(calc_coocc, total_sessions)
    
    # ✅ run summary query BEFORE closing the session
    result = session.run("MATCH ()-[r:CONNECTED_TO]->() RETURN count(r) AS edges;")
    print(f"Co-occ edges added: {result.single()['edges']}")

driver.close()
