import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os

# ---- Setup ----
load_dotenv()
password = os.getenv('PASSWORD')
driver = GraphDatabase.driver(os.getenv('NEO4J_URI', 'bolt://localhost:7687'), auth=("neo4j", password))

# ---- Page Config ----
st.set_page_config(page_title="SoundMatch", page_icon="🎵", layout="wide")

# ---- Custom CSS ----
st.markdown("""
    <style>
        body {
            background-color: #0e0e0e;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
        }
        .main {
            background-color: #0e0e0e;
        }
        h1, h2, h3, h4, h5 {
            color: #fff;
            font-weight: 700;
        }
        .stTextInput>div>div>input {
            background-color: #1b1b1b;
            color: white;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #008000;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #00b300;
        }
        .recommendation-box {
            background-color: #141414;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.1);
        }
        .placeholder-icon {
            font-size: 40px;
            color: #555;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title Section ----
st.markdown("<h1 style='text-align:center;'>🎧 SoundMatch</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#9c9c9c;'>Discover songs that flow together</p>", unsafe_allow_html=True)
st.markdown("---")

# ---- Layout ----
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Search for a Track")
    track = st.text_input(" ", placeholder="e.g., Taylor Swift - Anti-Hero")
    st.caption("Enter a track name to discover similar songs based on listening patterns")
    search = st.button("Search")

with col2:
    st.markdown("### Top Recommendations")
    recommendation_box = st.container()

# ---- Functionality ----
if search:
    with driver.session() as session:
        recs = session.run("""
            MATCH (e:Event {name: $track, type: 'play'})-[r:CONNECTED_TO]->(next:Event {type: 'play'})
            WITH next.name AS recommended_track, max(r.popularity) AS popularity
            RETURN recommended_track, popularity
            ORDER BY popularity DESC
            LIMIT 5
        """, track=track).data()

        if recs:
            rec_df = pd.DataFrame(recs)
            with recommendation_box:
                st.dataframe(rec_df, use_container_width=True)
        else:
            with recommendation_box:
                st.markdown("<div class='placeholder-icon'>🎵</div>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#777;'>No recommendations found — try another track.</p>", unsafe_allow_html=True)
else:
    with recommendation_box:
        st.markdown("<div class='placeholder-icon'>🎵</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#777;'>Search for a track to see recommendations</p>", unsafe_allow_html=True)

driver.close()
