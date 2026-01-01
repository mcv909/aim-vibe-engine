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
# 1. Pfade definieren
basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.dirname(basedir)

# 2. Suchliste für die .env erstellen
env_targets = [
    os.path.join(basedir, '.env'),
    os.path.join(parentdir, '.env')
]

# 3. .env laden
# Wir gehen die Liste durch. Das aktuelle Element heißt "target".
for target in env_targets:
    if os.path.exists(target):          # Prüfe das einzelne "target"
        load_dotenv(target, override=True) # Lade das einzelne "target"
        break                           # Stop, wenn eine gefunden wurde

VERSION = "v0.3.4-PRO-BETA"
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
# --- NEU: DESIGN INJEKTION ---
def apply_minimalist_theme():
    st.markdown("""
        <style>
        .stApp { background-color: #F8F9FA; color: #1B263B; }
        .brand-title { font-size: 3.5rem; font-weight: 200; letter-spacing: 0.6rem; color: #1B263B; margin-bottom: 0rem; }
        .brand-subtitle { font-size: 0.85rem; letter-spacing: 0.2rem; color: rgba(27, 38, 59, 0.5); margin-bottom: 2rem; text-transform: uppercase; }
        .anchor-box { 
            border: 1px solid rgba(27, 38, 59, 0.1); 
            padding: 1.5rem; 
            background-color: #FFFFFF; 
            border-radius: 2px;
            height: 100%;
        }
        .stick-figure { font-size: 30px; margin-bottom: 10px; }
        .pixelated { opacity: 0.2; }
        /* Buttons & Inputs */
        .stButton > button { border: 1px solid #1B263B; border-radius: 0px; background: transparent; color: #1B263B; width: 100%; }
        .stButton > button:hover { background: #1B263B; color: #F8F9FA; }
        hr { border: 0; border-top: 1px solid rgba(27, 38, 59, 0.15); }
        </style>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # 1. Config & Theme
    st.set_page_config(page_title=f"I AM | {VERSION}", page_icon="🎯", layout="wide")
    apply_minimalist_theme()
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 2. Beta-Schutz (unverändert)
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown('<p class="brand-title">I AM</p>', unsafe_allow_html=True)
        pwd_input = st.text_input("Access Key:", type="password")
        if st.button("Unlock"):
            if pwd_input == os.getenv("BETA_PASSWORD"):
                st.session_state["authenticated"] = True
                st.rerun()
        st.stop()

    # 3. Sidebar / Admin
    if st.sidebar.checkbox("Admin-Bereich"):
        show_admin_dashboard(client)

    # 4. Branding Header
    st.markdown('<p class="brand-title">I AM</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Architectural Intelligent Matching</p>', unsafe_allow_html=True)
    
    # 5. Der Qualitative Anker (Das neue Layout)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="anchor-box">
            <div class="stick-figure pixelated">👤</div>
            <p><strong>Vager Input</strong><br>
            Erzeugt ein generisches Rauschen. Die Architektur bleibt instabil.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="anchor-box">
            <div class="stick-figure">🧍‍♂️</div>
            <p><strong>Präzise DNA</strong><br>
            Je tiefer das Manifesto, desto schärfer die Resonanz. Qualität erzeugt Identität.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # 6. Eingabe-Maske (In den neuen Stil integriert)
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        u_name = sanitize_input(c1.text_input("Identität (Name):", placeholder="Marc"))
        u_loc = sanitize_input(c2.text_input("Präsenz (Ort):", placeholder="Obertshausen"))
        u_contact = sanitize_input(c3.text_input("Signal (Telegram):", placeholder="@handle"))
        
        manifesto = st.text_area("Manifesto (Deine Resonanz-DNA):", height=200, 
                                placeholder="Beschreibe deine Vision, deine Skills und deine Schwingung...")

    # 7. Matching Logik (dein bestehender Code)
    if st.button("RESONANZ ERZEUGEN"):
        if u_name and manifesto and u_contact:
            # ... (Hier folgt dein bestehender Code für Embeddings und DB-Speicherung) ...
            # [WICHTIG: Nutze hier deine bestehende Logik weiter]
            st.info("AIM analysiert die Geometrie...")
            # ...
            
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