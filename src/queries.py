from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv('PASSWORD')

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    auth=("neo4j", password)
)

def track_recs(tx, track):
    return tx.run("""
        MATCH (e:Event {name: $track, type: 'play'})-[r:CONNECTED_TO]->(next:Event {type: 'play'})
        WITH next.name AS recommended_track, max(r.popularity) AS popularity
        RETURN recommended_track, popularity
        ORDER BY popularity DESC
        LIMIT 5
    """, track=track).data()

with driver.session() as session:
    recs = session.execute_read(track_recs, 'Taylor Swift - Anti-Hero')
    print("Play-Only Recs for 'Taylor Swift - Anti-Hero':", recs)

driver.close()