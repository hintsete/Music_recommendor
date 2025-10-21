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

df = pd.read_csv('data/music_subset.csv')
df = df[df['Action'] == 'play']  # Play-only for eval

# Split: 80% train sessions
unique_sessions = df['Session_id'].unique()
train_sessions = unique_sessions[:int(0.8 * len(unique_sessions))]
test_sessions = unique_sessions[int(0.8 * len(unique_sessions)):]
test_df = df[df['Session_id'].isin(test_sessions)]

def get_recs(tx, last_eid):
    return tx.run("""
        MATCH (last:Event {eid: $last_eid, type: 'play'})-[r:CONNECTED_TO]->(next:Event {type: 'play'})
        RETURN next.name AS name, r.popularity AS popularity
        ORDER BY r.popularity DESC
        LIMIT 5
    """, last_eid=last_eid).data()

mrr_scores = []
with driver.session() as session:
    for _, test_group in test_df.groupby('Session_id'):
        if len(test_group) < 2:
            continue
        last_eid = str(test_group.iloc[-2]['Session_id']) + '_' + str(test_group.iloc[-2]['step'])
        true_next_name = test_group.iloc[-1]['SubCategory']

        recs = session.execute_read(get_recs, last_eid)
        rec_list = [rec['name'] for rec in recs]

        rank = rec_list.index(true_next_name) + 1 if true_next_name in rec_list else 0
        mrr_scores.append(1.0 / rank if rank > 0 else 0)

avg_mrr = np.mean(mrr_scores)
print(f"Play-Only Avg MRR: {avg_mrr:.3f}")

baseline_mrr = 1.0 / 5
print(f"Baseline MRR: {baseline_mrr:.3f}")

driver.close()
