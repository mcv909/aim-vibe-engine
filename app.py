import streamlit as st
import json
import os
import datetime
import uuid
import hashlib
import re
import html
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI
from dotenv import load_dotenv
import telebot
import psutil
from cryptography.fernet import Fernet

# --- INITIALISIERUNG & KONFIG ---
# Wir bestimmen den Ordner der app.py und den Ordner darüber
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)

# Wir prüfen beide Orte auf eine .env Datei
env_locations = [
    os.path.join(current_dir, '.env'),
    os.path.join(parent_dir, '.env')
]

for loc in env_locations:
    if os.path.exists(loc):
        load_dotenv(loc)
        break # Stoppt, sobald die erste .env gefunden wurde

VERSION = "v0.3.2-PRO-BETA"
APP_NAME = "AIM VIBE"

# --- SECURITY & VERSCHLÜSSELUNG ---
def get_cipher():
    """Nutzt den Key aus .env oder secrets.toml für AES-Verschlüsselung."""
    key = os.getenv("ENCRYPTION_KEY") or st.secrets.get("ENCRYPTION_KEY")
    if not key:
        st.error("🚨 KRITISCHER FEHLER: ENCRYPTION_KEY nicht gefunden!")
        st.stop()
    return Fernet(key.encode())

def encrypt_data(data):
    return get_cipher().encrypt(data.encode()).decode() if data else ""

def decrypt_data(token):
    try:
        return get_cipher().decrypt(token.encode()).decode()
    except Exception:
        return "[Entschlüsselungsfehler]"

def sanitize_input(text):
    if not text: return ""
    clean = re.sub(r"(DROP TABLE|DELETE FROM|<script|system\()", "[REDACTED]", text, flags=re.IGNORECASE)
    return html.escape(clean)

def hash_key(vibe_key):
    return hashlib.sha256(vibe_key.encode()).hexdigest()

# --- HELFER-FUNKTIONEN ---
def calculate_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def send_telegram_msg(msg, silent=False):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")

    if token and admin_id:
        try:
            bot = telebot.TeleBot(token)
            # Nur das int() lassen wir zur Sicherheit, da IDs immer Zahlen sind
            bot.send_message(int(admin_id), msg, parse_mode='Markdown', disable_notification=silent)
        except Exception as e:
            st.error(f"Telegram-Fehler: {e}")

# --- TEST-USER INJEKTOR ---
def inject_test_users(client):
    """Erzeugt Test-Profile für den Vibe-Check."""
    test_data = [
        {"name": "Techno Marc (Test)", "loc": "Lützow", "manifesto": "Ich liebe treibende Beats, ARM-Server und effizienten Code.", "contact": "@test_admin"},
        {"name": "Yoga Yvonne (Test)", "loc": "Hamburg", "manifesto": "Achtsamkeit, Meditation und spirituelle Energie sind mein Weg.", "contact": "@test_yoga"}
    ]
    
    db = []
    if os.path.exists('profiles_db.json'):
        with open('profiles_db.json', 'r') as f: db = json.load(f)

    for profile in test_data:
        emb = client.embeddings.create(input=profile['manifesto'], model="text-embedding-3-small").data[0].embedding
        record = {
            "name": encrypt_data(profile['name']),
            "gender": "m", "target_gender": "all",
            "loc": encrypt_data(profile['loc']),
            "contact": encrypt_data(profile['contact']),
            "vibe_key_hash": hash_key(str(uuid.uuid4())),
            "vector": emb,
            "timestamp": datetime.datetime.now().isoformat(),
            "is_test": True
        }
        db.append(record)
    
    with open('profiles_db.json', 'w') as f:
        json.dump(db, f, indent=2)
    st.success(f"{len(test_data)} Test-User erfolgreich injiziert!")

# --- UI: ADMIN BEREICH ---
def show_admin_dashboard(client):
    st.divider()
    st.subheader("🛡️ AIM-Vibe Engine - Admin Control")
    admin_pwd = st.text_input("Master Password", type="password")
    
    if admin_pwd == st.secrets["ADMIN_PASSWORD"]:
        st.success("Willkommen im Maschinenraum, Marc.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Server", "CAX11 ARM", "Hetzner")
        col2.metric("CPU", f"{psutil.cpu_percent()}%")
        col3.metric("RAM", f"{psutil.virtual_memory().percent}%")

        if st.button("🧪 Test-User (Seed) injizieren"):
            inject_test_users(client)

# --- MAIN APP ---
def main():
    st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎯", layout="wide")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Beta-Schutz
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 AIM-VIBE – Beta Access")
        pwd_input = st.text_input("Passwort:", type="password")
        if st.button("Unlock"):
            if pwd_input == os.getenv("BETA_PASSWORD"):
                st.session_state["authenticated"] = True
                st.rerun()
        st.stop()

    if st.sidebar.checkbox("Admin-Bereich"):
        show_admin_dashboard(client)

    st.title("🎯 AIM-VIBE > The Resonator")
    
    # Eingabe-Maske
    with st.container():
        c1, c2, c3 = st.columns(3)
        u_name = sanitize_input(c1.text_input("Dein Name:", placeholder="Marc"))
        u_loc = sanitize_input(c2.text_input("Standort:", placeholder="Lützow"))
        u_contact = sanitize_input(c3.text_input("Telegram (@username):"))
        manifesto = st.text_area("Dein Manifesto (Wer bist du?):", height=150)

    if st.button("Resonanz-DNA erzeugen"):
        if u_name and manifesto and u_contact:
            with st.status("🚀 Berechne Geometrie...") as status:
                v_key = str(uuid.uuid4())
                emb = client.embeddings.create(input=manifesto, model="text-embedding-3-small").data[0].embedding
                
                new_user = {
                    "name": encrypt_data(u_name), "loc": encrypt_data(u_loc),
                    "contact": encrypt_data(u_contact), "vibe_key_hash": hash_key(v_key),
                    "vector": emb, "timestamp": datetime.datetime.now().isoformat()
                }
                
                db = []
                if os.path.exists('profiles_db.json'):
                    with open('profiles_db.json', 'r') as f: db = json.load(f)
                db.append(new_user)
                with open('profiles_db.json', 'w') as f: json.dump(db, f, indent=2)
                
                status.update(label="✅ DNA verankert!", state="complete")
            
            st.success(f"Dein Vibe-Key: {v_key}")
            
            # Matching
            # --- VERBESSERTE ANALYSE ---
            st.subheader("🔮 Resonator-Analyse")
            matches_count = 0
            highest_score = 0
            
            # Fortschrittsbalken für das Feedback
            progress_bar = st.progress(0)
            
            for i, other in enumerate(db):
                if other.get('vibe_key_hash') == hash_key(v_key): continue
                
                score = calculate_similarity(emb, other['vector'])
                highest_score = max(highest_score, score)
                
                # Fortschritt aktualisieren
                progress_bar.progress((i + 1) / len(db))
                
                o_name = decrypt_data(other['name'])
                
                if score >= 0.88:
                    st.balloons()
                    st.success(f"🔥 Volltreffer mit {o_name}! (Resonanz: {score:.4f})")
                    send_telegram_msg(f"🚀 **Match!**\n{u_name} & {o_name} ({score:.4f})")
                    matches_count += 1
                elif 0.82 <= score < 0.88:
                    st.info(f"📡 Nahe Resonanz erkannt: {score:.4f} (mit {o_name})")
                    send_telegram_msg(f"🔍 **Fast-Match:** {u_name} & {o_name} ({score:.4f})", silent=True)

            if matches_count == 0:
                st.warning(f"Aktuell keine Resonanz über 0.88. Höchster Wert im System: {highest_score:.4f}")
        else:
            st.warning("Bitte Name, Standort, Telegram und Manifesto ausfüllen.")

if __name__ == "__main__":
    main()