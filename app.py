import streamlit as st
import json
import os
import datetime
import time
import uuid
import hashlib
import re
import html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI
from dotenv import load_dotenv

# --- INITIALISIERUNG (Universal-Safe) ---
# 1. Lokale .env laden (macht lokal nichts kaputt, wenn sie fehlt)
load_dotenv()

# 2. Key abrufen: os.getenv schaut erst im System (Cloud Secrets) 
# und dann in der durch load_dotenv befüllten Umgebung nach.
api_key = os.getenv("OPENAI_API_KEY")

# 3. Client initialisieren
client = OpenAI(api_key=api_key)

# --- KONFIGURATION & VERSIONIERUNG ---
VERSION = "v0.2.6-DEV"
APP_NAME = "AIM VIBE"
load_dotenv()
client = OpenAI()

# --- SICHERHEITS-FUNKTIONEN ---
def sanitize_input(text):
    if not text: return ""
    forbidden = [r"DROP TABLE", r"DELETE FROM", r"<script", r"system\("]
    for pattern in forbidden:
        if re.search(pattern, text, re.IGNORECASE):
            st.error("Hacker? Deine Mudda!")
            st.stop()
    return html.escape(text)

def hash_key(vibe_key):
    """Erzeugt einen SHA-256 Hash des Vibe-Keys zur sicheren Speicherung."""
    return hashlib.sha256(vibe_key.encode()).hexdigest()

# --- MATHEMATIK & VISUALISIERUNG ---
def calculate_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def plot_vibe_sphere(user_vec, match_vec, match_name):
    v1 = np.array(user_vec[:3]) / np.linalg.norm(user_vec[:3])
    v2 = np.array(match_vec[:3]) / np.linalg.norm(match_vec[:3])
    fig = go.Figure()
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x, y, z = np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v)
    fig.add_trace(go.Surface(x=x, y=y, z=z, opacity=0.1, showscale=False, hoverinfo='skip'))
    fig.add_trace(go.Scatter3d(x=[0, v1[0]], y=[0, v1[1]], z=[0, v1[2]], mode='lines+markers', line=dict(color='blue', width=6), name="Deine DNA"))
    fig.add_trace(go.Scatter3d(x=[0, v2[0]], y=[0, v2[1]], z=[0, v2[2]], mode='lines+markers', line=dict(color='red', width=6), name=match_name))
    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0, r=0, b=0, t=0), height=400)
    return fig

# --- MAIN ---
def main():
    st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎯", layout="wide")
    
    with st.sidebar:
        st.title(f"🛠 {APP_NAME} Control")
        st.info(f"Version: {VERSION}")
        
        # --- LÖSCH-INTERFACE ---
        st.write("---")
        st.subheader("🗑 Profil löschen")
        delete_key = st.text_input("Vibe-Key eingeben:", type="password", help="Gib hier deine UUID ein, um dein Profil zu entfernen.")
        if st.button("Profil unwiderruflich löschen"):
            if delete_key:
                hashed_input = hash_key(delete_key)
                if os.path.exists('profiles_db.json'):
                    with open('profiles_db.json', 'r', encoding='utf-8') as f:
                        db = json.load(f)
                    
                    new_db = [p for p in db if p.get('vibe_key_hash') != hashed_input]
                    
                    if len(new_db) < len(db):
                        with open('profiles_db.json', 'w', encoding='utf-8') as f:
                            json.dump(new_db, f, ensure_ascii=False, indent=2)
                        st.success("Dein Profil wurde aus dem 1.536-dimensionalen Raum entfernt.")
                    else:
                        st.error("Key ungültig oder Profil nicht gefunden.")
            else:
                st.warning("Bitte gib einen Key ein.")

    st.title(f"🎯 {APP_NAME} – The Resonator")
    
    # 1. IDENTIFIKATION (PFLICHTFELDER)
    col1, col2, col3 = st.columns(3)
    with col1:
        user_name = st.text_input("Name:", placeholder="Marc")
        gender = st.selectbox("Ich bin:", ["m", "w", "d"])
    with col2:
        search_map = {"Partnerin (w)": "w", "Partner (m)": "m", "Freunde (egal)": "all"}
        search_choice = st.selectbox("Ich suche:", list(search_map.keys()))
        target_gender = search_map[search_choice]
        location = st.text_input("Standort (Stadt):", placeholder="z.B. Lützow")
    with col3:
        messenger = st.selectbox("Rückkanal:", ["Telegram", "WhatsApp"])
        contact_value = st.text_input(f"Dein {messenger}-Handle / Nummer:")

    manifesto_raw = st.text_area("Dein Manifesto:", height=150)
    
    if st.button("Resonanz-DNA erzeugen"):
        # Validierung der Pflichtfelder
        if not user_name or not manifesto_raw or not location or not contact_value:
            st.warning("Moin! Ohne Name, Manifesto, Standort und Kontaktdaten kann die Matching-Magie nicht starten.")
        else:
            with st.status("🚀 AIM berechnet Geometrie...", expanded=True) as status:
                # UUID & Hash Generierung
                new_vibe_key = str(uuid.uuid4())
                vibe_hash = hash_key(new_vibe_key)
                
                st.session_state['vibe_key'] = new_vibe_key
                st.session_state['user_data'] = {
                    "name": sanitize_input(user_name),
                    "gender": gender, "target_gender": target_gender,
                    "loc": sanitize_input(location), "messenger": messenger,
                    "contact": sanitize_input(contact_value),
                    "vibe_key_hash": vibe_hash
                }
                
                # Vektorisierung
                embedding = client.embeddings.create(input=manifesto_raw, model="text-embedding-3-small").data[0].embedding
                st.session_state['user_vector'] = embedding
                
                # Speicherung in der lokalen DB (Simuliert für Beta)
                if os.path.exists('profiles_db.json'):
                    with open('profiles_db.json', 'r', encoding='utf-8') as f:
                        db = json.load(f)
                else:
                    db = []
                
                db.append({**st.session_state['user_data'], "vector": embedding})
                with open('profiles_db.json', 'w', encoding='utf-8') as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
                
                status.update(label="✅ DNA verankert!", state="complete", expanded=False)
            
            # Anzeige des Vibe-Keys
            st.success("Deine Resonanz-DNA wurde erzeugt!")
            st.code(f"DEIN VIBE-KEY: {new_vibe_key}", language="text")
            st.warning("⚠️ WICHTIG: Speichere diesen Key! Nur mit ihm kannst du dein Profil später wieder löschen.")
            
            # Monty Python Celebration
            if os.path.exists("OHcB.gif"):
                st.image("OHcB.gif", use_container_width=True)

    # ... (Matching Logik bleibt wie gehabt)

if __name__ == "__main__":
    main()