import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_music_response(track, recs):
    try:
        rec_list = ", ".join([r['recommended_track'] for r in recs])
        prompt = (
            f"You have an amazing taste! You searched for '{track}', "
            f"and based on your vibe, you might also enjoy {rec_list}. "
            f"Write this in an engaging, conversational tone."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate LLM response: {e}"
