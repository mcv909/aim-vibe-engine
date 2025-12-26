import streamlit as st
import json
import os
import datetime
import time
import re
import html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI
from dotenv import load_dotenv

# --- KONFIGURATION & VERSIONIERUNG ---
VERSION = "v0.2.0-DEV"
APP_NAME = "AIM VIBE"
load_dotenv()
client = OpenAI()

# --- SICHERHEITS-LAYER ---
def sanitize_input(text):
    if not text: return ""
    forbidden = [r"DROP TABLE", r"DELETE FROM", r"<script", r"system\("]
    for pattern in forbidden:
        if re.search(pattern, text, re.IGNORECASE):
            st.error("Hacker? Deine Mudda!")
            st.stop()
    return html.escape(text)

# --- MATHEMATIK & VISUALISIERUNG ---
def calculate_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def plot_vibe_sphere(user_vec, match_vec, match_name):
    """Visualisiert zwei Vektoren auf einer 3D-Einheitskugel."""
    # Projektion der 1536D auf 3D (vereinfacht für v0.2.0)
    v1 = np.array(user_vec[:3]) / np.linalg.norm(user_vec[:3])
    v2 = np.array(match_vec[:3]) / np.linalg.norm(match_vec[:3])
    
    fig = go.Figure()
    # Zeichne die Einheitskugel (Gitternetz)
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)
    fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.1, showscale=False, hoverinfo='skip'))

    # Vektor Marc (Du)
    fig.add_trace(go.Scatter3d(x=[0, v1[0]], y=[0, v1[1]], z=[0, v1[2]], 
                               mode='lines+markers', line=dict(color='blue', width=6), name="Deine DNA"))
    # Vektor Match
    fig.add_trace(go.Scatter3d(x=[0, v2[0]], y=[0, v2[1]], z=[0, v2[2]], 
                               mode='lines+markers', line=dict(color='red', width=6), name=match_name))
    
    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      margin=dict(l=0, r=0, b=0, t=0), height=400)
    return fig

# --- KI-EXTRAKTION ---
def extract_and_vectorize_pillars(text):
    prompt = f"Extrahiere JSON: {{\"A\": \"Gerechtigkeit\", \"B\": \"Resilienz\", \"C\": \"Musik\", \"D\": \"Adams\"}} Manifesto: {text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    data = json.loads(response.choices[0].message.content)
    return [{"category": "Gesamt", "vector": client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding}]

def show_monty_celebration():
    """Zeigt die klatschenden Omas ohne Deprecation-Warnung."""
    # Der Dateiname muss exakt celebration.gif lauten (wie dein Upload)
    gif_path = "celebration.gif" 
    if os.path.exists(gif_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # FIX: use_container_width statt use_column_width
            st.image(gif_path, use_container_width=True)
    else:
        st.balloons()

# --- MAIN (v0.2.2-DEV) ---
def main():
    st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎯", layout="wide")
    
    with st.sidebar:
        st.title(f"🛠 {APP_NAME} Control")
        st.info(f"Version: {VERSION} (Filtered)")
        if st.button("System-Reset"):
            st.session_state.clear()
            st.rerun()

    st.title(f"🎯 {APP_NAME} – The Resonator")
    
    # 1. IDENTIFIKATION
    col1, col2, col3 = st.columns(3)
    with col1:
        user_name = st.text_input("Name:", placeholder="Marc")
        gender = st.selectbox("Ich bin:", ["m", "w", "d"])
    with col2:
        # Mapping für die Suche: Was der User wählt -> Was wir in der DB suchen
        search_map = {"Partnerin (w)": "w", "Partner (m)": "m", "Freunde (egal)": "all"}
        search_choice = st.selectbox("Ich suche:", list(search_map.keys()))
        target_gender = search_map[search_choice]
        
        location = st.text_input("Standort (Stadt):", placeholder="z.B. Lützow")
    with col3:
        messenger = st.selectbox("Rückkanal:", ["Telegram", "WhatsApp", "Keiner"])

    manifesto_raw = st.text_area("Dein Manifesto:", height=150)
    
    if st.button("Resonanz-DNA erzeugen"):
        if user_name and manifesto_raw and location:
            with st.status("🚀 AIM berechnet Geometrie...", expanded=True) as status:
                st.session_state['user_data'] = {
                    "name": sanitize_input(user_name),
                    "gender": gender, 
                    "target_gender": target_gender, # Wir speichern das Ziel-Geschlecht
                    "loc": sanitize_input(location),
                    "manifesto": sanitize_input(manifesto_raw)
                }
                # Vektorisierung (vereinfacht für Demo)
                st.session_state['user_vector'] = client.embeddings.create(input=manifesto_raw, model="text-embedding-3-small").data[0].embedding
                status.update(label="✅ DNA verankert!", state="complete", expanded=False)
            
            # DIE NEUE ANIMATION
            show_monty_celebration()
            
        else:
             st.warning("Bitte Name, Manifesto und Standort ausfüllen!")

    # 2. GEFILTERTES MATCHING
    if 'user_vector' in st.session_state and os.path.exists('profiles_db.json'):
        user_loc = st.session_state['user_data']['loc']
        target_g = st.session_state['user_data']['target_gender']
        
        st.divider()
        st.subheader(f"🔍 Top-Matches in '{user_loc}'")
        
        if st.button("Gefilterten Vibe-Abgleich starten"):
            with open('profiles_db.json', 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            # --- DIE ROBUSTE FILTER-LOGIK (v0.2.3) ---
            filtered_db = []
            for p in db:
                # Wir nutzen .get(), um Abstürze bei fehlenden Keys zu vermeiden
                p_loc = p.get('loc', 'Unbekannt') 
                p_gender = p.get('gender', 'd')
                
                # 1. Standort-Check
                loc_match = (p_loc.lower() == user_loc.lower())
                
                # 2. Gender-Check
                if target_g == "all":
                    gender_match = True
                else:
                    gender_match = (p_gender == target_g)
                
                if loc_match and gender_match:
                    filtered_db.append(p)
            # -----------------------------------------

            if not filtered_db:
                st.warning(f"Keine Resonanzen in {user_loc} für deine Suche gefunden. (Probier mal 'Frankfurt' oder ändere die Suche)")
            else:
                # Berechnung nur für gefilterte Ergebnisse
                matches = sorted([{"name": p['name'], "vec": p['vector'], "score": calculate_similarity(st.session_state['user_vector'], p['vector'])} for p in filtered_db], 
                                 key=lambda x: x['score'], reverse=True)

                for i, m in enumerate(matches[:3]): # Top 3 der gefilterten
                    with st.expander(f"Platz {i+1}: {m['name']} ({round(m['score']*100, 2)}% Resonanz)"):
                        st.plotly_chart(plot_vibe_sphere(st.session_state['user_vector'], m['vec'], m['name']), use_container_width=True)

if __name__ == "__main__":
    main()