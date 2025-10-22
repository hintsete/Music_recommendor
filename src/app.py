import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
from dotenv import load_dotenv
import os
from llm_response import generate_music_response

# ---- Setup ----
load_dotenv()
password = os.getenv('PASSWORD')
driver = GraphDatabase.driver(os.getenv('NEO4J_URI', 'bolt://localhost:7687'), auth=("neo4j", password))

# ---- Page Config ----
st.set_page_config(page_title="SoundMatch", page_icon="🎵", layout="wide")

# ---- Custom CSS ----
st.markdown("""
    <style>
        body { background-color: #0e0e0e; color: #ffffff; font-family: 'Inter', sans-serif; }
        h1, h2, h3, h4, h5 { color: #fff; font-weight: 700; }
        .stTextInput>div>div>input { background-color: #1b1b1b; color: white; border-radius: 10px; }
        .stButton>button { background-color: #008000; color: white; border-radius: 8px; border: none; padding: 0.5rem 1rem; font-weight: 500; }
        .stButton>button:hover { background-color: #00b300; }
        .recommendation-box { background-color: #141414; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0, 255, 0, 0.1); }
        .rec-row { display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #1b1b1b; border-radius: 8px; }
        .rec-info { flex: 1; }
        .rec-link { color: #1db954; text-decoration: none; }
        .rec-link:hover { text-decoration: underline; }
        .music-icon { font-size: 32px; margin-right: 15px; }
        .llm-expl { background-color: #1b1b1b; padding: 15px; border-radius: 10px; color: #ddd; }
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

# ---- Utility Functions ----
def get_youtube_link(track):
    search_query = f"{track} official audio"
    yt_base = "https://www.youtube.com/results?search_query="
    return yt_base + search_query.replace(' ', '+')

# ---- Main Functionality ----
if search:
    with driver.session() as session:
        recs = session.run("""
            MATCH (e:Event {name: $track, type: 'play'})-[r:CONNECTED_TO]->(next:Event {type: 'play'})
            WITH next.name AS recommended_track, max(r.popularity) AS popularity
            RETURN recommended_track, popularity
            ORDER BY popularity DESC
            LIMIT 5
        """, track=track).data()

        with recommendation_box:
            if recs:
                st.markdown("<div class='recommendation-box'>", unsafe_allow_html=True)
                for row in recs:
                    rec_track = row['recommended_track']
                    pop = row['popularity']
                    yt_url = get_youtube_link(rec_track)
                    st.markdown(f"""
                        <div class='rec-row'>
                            <div class='music-icon'>🎵</div>
                            <div class='rec-info'>
                                <strong>{rec_track}</strong> <span style='color:#888'>(Popularity: {pop})</span><br>
                                <a href="{yt_url}" target="_blank" class="rec-link">▶️ Play on YouTube</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # LLM Expl
                with st.spinner("✨ Crafting AI message..."):
                    llm_response = generate_music_response(track, recs)
                st.markdown("---")
                st.markdown("#### 🎶 AI Companion Says:")
                st.markdown(f"<div class='llm-expl'>{llm_response}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='text-align:center; color:#777;'>No recommendations found — try another track.</p>", unsafe_allow_html=True)
else:
    with recommendation_box:
        st.markdown("<p style='text-align:center; color:#777;'>Search for a track to see recommendations</p>", unsafe_allow_html=True)

driver.close()
