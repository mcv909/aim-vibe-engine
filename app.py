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
import telebot # Muss in requirements.txt stehen!

# --- TELEGRAM LOGIK (Sauber getrennt) ---

def log_fast_match_to_admin(user_a, user_b, score):
    """Sendet eine lautlose Info bei Beinahe-Resonanz (0.82 - 0.87)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")
    if not token or not admin_id: 
        return
    
    bot = telebot.TeleBot(token)
    msg = (f"🔍 **Fast-Match Monitoring**\n\n"
           f"Präzision: **{score:.2f}**\n"
           f"Zwischen: {user_a['name']} & {user_b['name']}\n"
           f"Status: Unter 0.88 - kein automatischer Kontakt.")
    
    try:
        # disable_notification=True macht die Nachricht lautlos
        bot.send_message(admin_id, msg, parse_mode='Markdown', disable_notification=True)
    except Exception as e:
        print(f"Monitoring-Fehler: {e}")

def trigger_match_alarm(user_a, user_b, score):
    """Sendet einen echten Alarm bei hoher Resonanz (>= 0.88)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")
    if not token or not admin_id: 
        return
        
    bot = telebot.TeleBot(token)
    msg = (f"🚀 **Resonanz-Alarm!**\n\n"
           f"Mathematische Präzision: **{score:.2f}**\n\n"
           f"👤 **{user_a['name']}** ({user_a['loc']})\n"
           f"    ↔️\n"
           f"👤 **{user_b['name']}** ({user_b['loc']})\n\n"
           f"Die Geometrie der Gedanken passt! Kontakt via Telegram: {user_b['contact']}")
    
    try:
        bot.send_message(admin_id, msg, parse_mode='Markdown')
    except Exception as e:
        st.error(f"Telegram-Fehler: {e}")

# --- INITIALISIERUNG FOLGT HIER ---
  
    if not token or not admin_id:
        return # Sicherheit, falls Keys fehlen
        
    bot = telebot.TeleBot(token)
    
    # Die Nachricht, die DU als Admin (oder später die User) bekommst
    msg = (f"🚀 **Resonanz-Alarm!**\n\n"
           f"Mathematische Präzision: **{score:.2f}**\n\n"
           f"👤 **{user_a['name']}** ({user_a['location']})\n"
           f"    ↔️\n"
           f"👤 **{user_b['name']}** ({user_b['location']})\n\n"
           f"Die Geometrie der Gedanken passt! Kontakt via Telegram: {user_b['contact']}")
    
    try:
        bot.send_message(admin_id, msg, parse_mode='Markdown')
    except Exception as e:
        st.error(f"Telegram-Fehler: {e}")

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
    
    # --- 1. BETA-SCHUTZ (Sicherung der Resonanz) ---
    BETA_PASSWORD = os.getenv("BETA_PASSWORD")
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 AIM-VIBE – Beta Access")
        st.write("Moin! Diese Version ist aktuell nur für geladene Pioniere zugänglich.")
        pwd_input = st.text_input("Bitte gib das Beta-Passwort ein:", type="password")
        if st.button("Unlock matching magic"):
            if pwd_input == BETA_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Falsches Passwort. Die Resonanz bleibt verwehrt.")
        st.stop()

    # --- 2. BRANDING & TITEL ---
    st.title("🎯 AIM-VIBE > The Resonator")
    st.subheader("Finde deine semantische Resonanz im 1.536-dimensionalen Raum")

    # --- 3. DER VIBE-GUIDE (Erklärungstext) ---
    with st.expander("📖 Wie funktioniert die Matching-Magie? (Hier klicken)", expanded=True):
        st.markdown("""
        **Was bringt es dir?** Vergiss oberflächliches Swipen. Wir finden Menschen, die auf derselben Frequenz schwingen wie du – basierend auf deinen Werten und Gedanken.
        
        **Die Technik:**
        1. **Manifesto:** Du schreibst, wer du bist. Was dir wichtig ist, was nicht; Was du magst und was nicht; Schreib einfach ;)
        2. **DNA:** AIM wandelt deinen Text in einen hochdimensionalen Vektor um. Aus deinen Gedanken wird Geometrie.
        3. **Matching:** Wir berechnen die **Cosinus-Ähnlichkeit** zwischen dir und allen anderen Profilen.            
        
        **Der Ablauf:**
        Bei einer Resonanz von über **0.88** schlägt der Resonator an. 
        **Wichtig:** Aktuell nutzen wir exklusiv **Telegram** für die Benachrichtigung. Dein Match erhält dein Handle und kann den ersten Schritt machen.
        
        **Feedback:**
        Da wir die Magie nur berechnen, aber nicht 'sehen', brauchen wir dich: Schreib uns kurz, ob der Vibe beim Match gepasst hat!
        """)

    # --- 4. DAS INTERFACE (Eingabe) ---
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        user_name = st.text_input("Dein Name:", placeholder="Marc")
        gender = st.selectbox("Ich bin:", ["m", "w", "d"])
    with col2:
        search_map = {"Partnerin (w)": "w", "Partner (m)": "m", "Freunde (egal)": "all"}
        search_choice = st.selectbox("Ich suche:", list(search_map.keys()))
        target_gender = search_map[search_choice]
        location = st.text_input("Standort (Stadt):", placeholder="z.B. Lützow")
    with col3:
        st.info("💡 Beta-Kanal: Telegram")
        # Wir definieren die Variable hier fest, damit sie unten bekannt ist
        messenger = "Telegram" 
        contact_value = st.text_input("Dein Telegram-Handle (@username):")
        if contact_value and not contact_value.startswith("@"):
            st.caption("Tipp: Handles starten meist mit @")

    manifesto_raw = st.text_area("Dein Manifesto (Was macht dich aus?):", height=200)
    
    # --- 5. LOGIK-TRIGGER ---
    
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

    # --- 6. MATCHING ANALYSE ---
            st.write("---")
            st.subheader("🔮 Die Resonator-Analyse")
            
            matches_found = 0
            # Wir laden die DB frisch, um alle (inkl. dem neuen Profil) zu haben
            if os.path.exists('profiles_db.json'):
                with open('profiles_db.json', 'r', encoding='utf-8') as f:
                    all_profiles = json.load(f)
                
                for other in all_profiles:
                    # Nicht mit sich selbst vergleichen (via Hash)
                    if other['vibe_key_hash'] == vibe_hash:
                        continue
                    
                    # Mathematik der Resonanz
                    score = calculate_similarity(embedding, other['vector'])
                    
                    # A: Echter Volltreffer
                    if score >= 0.88:
                        trigger_match_alarm(st.session_state['user_data'], other, score)
                        st.success(f"🔥 Volltreffer! Du hast eine hohe Resonanz mit {other['name']}!")
                        st.plotly_chart(plot_vibe_sphere(embedding, other['vector'], other['name']))
                        matches_found += 1
                    
                    # B: Fast-Match Monitoring (nur für Admin)
                    elif 0.82 <= score < 0.88:
                        log_fast_match_to_admin(st.session_state['user_data'], other, score)
            
            if matches_found == 0:
                st.info("Aktuell schwingt noch niemand exakt auf deiner Frequenz. Aber keine Sorge: Deine DNA ist verankert und wartet auf das passende Gegenstück!")

if __name__ == "__main__":
    main()