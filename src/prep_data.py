import pandas as pd

# ---- Load Excel ----
df = pd.read_excel('data/music_subset.xlsx')
print("Raw columns:", df.columns.tolist())
print("Raw head:\n", df.head())
print("Raw shape:", df.shape)
print("Unique sessions:", df['Session_id'].nunique())

# ---- Clean & prep ----
df = df.dropna(subset=['Session_id', 'DateTime', 'Action'])
df['DateTime'] = pd.to_datetime(df['DateTime'])
df = df.sort_values(['Session_id', 'DateTime'])

# ---- Add step (order per session) ----
df['step'] = df.groupby('Session_id').cumcount() + 1

# ---- Subset: First 100 sessions, max 10 events/session ----
df_subset = df.groupby('Session_id').head(10).reset_index(drop=True)
df_subset.to_csv('data/music_subset.csv', index=False)
print("Subset shape:", df_subset.shape)
print("Subset head:\n", df_subset.head())
print("Action distribution:\n", df_subset['Action'].value_counts())

# ---- Pre-compute session starts/durations ----
session_starts = df_subset.groupby('Session_id')['DateTime'].agg(['min', 'max']).reset_index()
session_starts['start_time'] = session_starts['min']
session_starts['duration'] = (session_starts['max'] - session_starts['min']).dt.total_seconds()
session_starts = session_starts[['Session_id', 'start_time', 'duration']]
session_starts.to_csv('data/session_starts.csv', index=False)

# ---- Categories (Genre as Category, SubCategory as Artist - Track) ----
cat_df = df_subset[['Category', 'SubCategory']].drop_duplicates().reset_index(drop=True)
cat_df['catid'] = 'c' + cat_df.index.astype(str)
cat_df['name'] = cat_df['Category'] + ' - ' + cat_df['SubCategory']
cat_df['level'] = 1
cat_df.to_csv('data/categories_music.csv', index=False)
print("Categories saved:", len(cat_df), "unique")

print("\n---- Splitting Train/Test Sessions ----")
unique_sessions = df_subset['Session_id'].unique()
train_sessions = unique_sessions[:int(0.8 * len(unique_sessions))]
test_sessions = unique_sessions[int(0.8 * len(unique_sessions)):]

train_df = df_subset[df_subset['Session_id'].isin(train_sessions)]
test_df = df_subset[df_subset['Session_id'].isin(test_sessions)]

# Save the split files
train_df.to_csv('data/train_music.csv', index=False)
test_df.to_csv('data/test_music.csv', index=False)

print(f"Train sessions: {len(train_sessions)}, Test sessions: {len(test_sessions)}")
print("Train shape:", train_df.shape, "Test shape:", test_df.shape)
print("Train Action distribution:\n", train_df['Action'].value_counts())
print("Test Action distribution:\n", test_df['Action'].value_counts())
