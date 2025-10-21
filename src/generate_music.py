import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

np.random.seed(42)
random.seed(42)

num_sessions = 200
events_per_session = random.choices(range(3, 6), k=num_sessions)  # 3-5 events/session

genres = ['Ethiopiques', 'Pop', 'Hip Hop', 'Rock', 'Jazz']
artists_tracks = {
    'Ethiopiques': [('Mulatu Astatke', 'Yekermo Sew'), ('Hailu Mergia', 'Tezeta'), ('Aster Aweke', 'Menew'), ('Neway Debebe', 'Yene Alem')],
    'Pop': [('Lana Del Rey', 'Video Games'), ('Taylor Swift', 'Anti-Hero'), ('Billie Eilish', 'Ocean Eyes'), ('Ariana Grande', 'thank u, next')],
    'Hip Hop': [('Lauryn Hill', 'I Gotta find piece of mind'), ('Erykah Badu', 'On & On'), ('Kendrick Lamar', 'Love.'), ('J. Cole', 'Middle Child')],
    'Rock': [('Arctic Monkeys', 'Do I Wanna Know?'), ('The Strokes', 'Last Nite'), ('Foo Fighters', 'Everlong'), ('The Killers', 'Mr. Brightside')],
    'Jazz': [('Miles Davis', 'So What'), ('Kamasi Washington', 'Truth'), ('John Coltrane', 'A Love Supreme'), ('Herbie Hancock', 'Cantaloupe Island')]
}

data = []
current_session = 1
base_time = datetime(2025, 10, 1)

for session in range(num_sessions):
    session_id = f"sess_{current_session:03d}"
    user_id = random.randint(10000000000, 99999999999)
    session_start = base_time + timedelta(days=random.randint(0, 30))
    genre = random.choice(genres)
    available_tracks = len(artists_tracks[genre])
    k = min(events_per_session[session], available_tracks)  # Fix: Cap to available tracks
    session_tracks = random.sample(artists_tracks[genre], k=k)  # Same genre per session
    
    for step in range(k):
        time_delta = timedelta(minutes=step * random.randint(2, 5))
        dt = session_start + time_delta
        artist, track = session_tracks[step]
        action = random.choice(['play', 'skip'])
        subcategory = f"{artist} - {track}"
        quantity = random.choice([1, 2]) if action == 'play' else np.nan
        rate = random.uniform(0.99, 4.99) if pd.notna(quantity) else np.nan
        total_price = quantity * rate if pd.notna(quantity) and pd.notna(rate) else np.nan
        
        data.append({
            'User_id': user_id,
            'Session_id': session_id,
            'DateTime': dt,
            'Category': genre,
            'SubCategory': subcategory,
            'Action': action,
           
            
        })
    
    current_session += 1

df = pd.DataFrame(data)
df.to_excel('data/music_subset.xlsx', index=False)
print(df.head(10))
print(f"Generated {len(df)} events across {num_sessions} sessions.")
print("Action distribution:\n", df['Action'].value_counts())
print("Unique sessions:", df['Session_id'].nunique())