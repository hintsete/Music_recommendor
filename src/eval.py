import numpy as np
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


df = pd.read_csv('data/test_music.csv')
df = df[df['Action'] == 'play']  # only 'play' actions for evaluation

print(f"Loaded {len(df)} play events from {df['Session_id'].nunique()} test sessions.")

def get_recs(tx, last_eid, top_n=5):
    query = """
        MATCH (last:Event {eid: $last_eid, type: 'play'})-[r:CONNECTED_TO]->(next:Event {type: 'play'})
        RETURN next.name AS name, r.popularity AS popularity
        ORDER BY r.popularity DESC
        LIMIT $top_n
    """
    return tx.run(query, last_eid=last_eid, top_n=top_n).data()

# ---- MRR Evaluation ----
mrr_scores = []
with driver.session() as session:
    for session_id, group in df.groupby('Session_id'):
        if len(group) < 2:
            continue  # need at least two events to predict the next

        group = group.sort_values('step').reset_index(drop=True)

    
        last_eid = f"{group.iloc[-2]['Session_id']}_{group.iloc[-2]['step']}"
        true_next_name = group.iloc[-1]['SubCategory']

        recs = session.execute_read(get_recs, last_eid)
        rec_list = [rec['name'] for rec in recs]

        # Compute reciprocal rank
        if true_next_name in rec_list:
            rank = rec_list.index(true_next_name) + 1
            rr = 1.0 / rank
        else:
            rr = 0.0

        mrr_scores.append(rr)

if mrr_scores:
    avg_mrr = np.mean(mrr_scores)
else:
    avg_mrr = 0.0

print(f"\n🎧 Play-Only Avg MRR (Test Set): {avg_mrr:.3f}")

baseline_mrr = 1.0 / 5
print(f" Baseline MRR : {baseline_mrr:.3f}")

driver.close()
