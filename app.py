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

VERSION = "v0.4.1-ARCHITECT"
APP_NAME = "I AM"  # Hier direkt das neue Branding setzen

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
# --- NEU: DESIGN INJEKTION (Das volle AIM-Vibe CSS) ---
def apply_minimalist_theme():
    st.markdown(f"""
        <style>
        /* Grundlayout */
        .stApp {{ background-color: #F8F9FA; color: #222; }}
        
        /* Branding Header */
        .brand-header {{
            text-align: center;
            padding: 40px 0 20px 0;
        }}
        .brand-title {
            font-size: 7rem;
            font-weight: 900;
            letter-spacing: 0.5rem;
            margin: 0;
            line-height: 1.1;
            color: #000;
            text-transform: uppercase;
            display: block;
        }}
        .brand-subtitle {{
            font-size: 1.1rem;
            color: #777;
            font-weight: 300;
            margin-top: 10px;
        }}

        /* Mona Lisa & Visual Anchor */
        .visual-anchor {{
            display: flex;
            flex-direction: column;
            gap: 25px;
            margin-top: 54px; /* Exakter Versatz für Oberkanten-Alignment */
        }}
        .m-box {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            height: 100px;
        }}
        .m-img-container {{
            width: 100px; height: 100px;
            overflow: hidden;
            border-radius: 4px;
            border: 1px solid #eee;
            flex-shrink: 0;
        }}
        .m-img-container img {{ width: 100%; height: 100%; object-fit: cover; }}
        .img-low img {{ filter: grayscale(100%) blur(8px) contrast(200%); transform: scale(1.1); }}
        .img-high img {{ filter: grayscale(100%) contrast(110%); }}

        /* Typo-Simulation */
        .m-skeleton {{
            flex-grow: 1;
            background-image: repeating-linear-gradient(
                to bottom, #e0e0e0, #e0e0e0 12px, transparent 12px, transparent 22px
            );
        }}
        .sk-low {{ height: 34px; width: 40%; }}
        .sk-high {{ height: 100%; width: 90%; }}

        /* Streamlit Widgets anpassen */
        .stTextArea textarea {{ background-color: #fafafa !important; border: 2px solid #e0e0e0 !important; }}
        .stTextInput input {{ background-color: #fafafa !important; border: 2px solid #e0e0e0 !important; }}
        
        /* Der schwarze Button */
        div.stButton > button {{
            background-color: #000 !important;
            color: #fff !important;
            border: none !important;
            padding: 20px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            width: 100% !important;
            border-radius: 0px !important;
        }}
        
        /* Footer Box */
        .footer-box {{
            background-color: #e9ecef;
            padding: 30px;
            margin-top: 50px;
            font-size: 0.9rem;
            color: #444;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # 1. Config & Theme
    VERSION_VIBE = "v0.4.0-AIM-VIBE"
    st.set_page_config(page_title=f"I AM | AIM", page_icon="🎯", layout="wide")
    apply_minimalist_theme()
    
    # OpenAI Client Initialisierung
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 2. Beta-Schutz (unverändert)
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown('<div class="brand-header"><p class="brand-title">[i am] | AIM</p></div>', unsafe_allow_html=True)
        pwd_input = st.text_input("Access Key:", type="password")
        if st.button("Unlock"):
            if pwd_input == os.getenv("BETA_PASSWORD") or pwd_input == "letmein": # Backup für Test
                st.session_state["authenticated"] = True
                st.rerun()
        st.stop()

    # 3. Sidebar Admin (Optional)
    if st.sidebar.checkbox("Admin-Bereich"):
        show_admin_dashboard(client)

    # 4. Branding Header
    st.markdown(f"""
        <div class="brand-header">
            <p class="brand-title">[i am] | AIM</p>
            <p class="brand-subtitle">AI-Matching basierend auf Resonanz, nicht auf Checklisten.</p>
            <p style="color: rgba(0,0,0,0.2); font-size: 0.7rem; letter-spacing: 0.1rem; margin-top:10px;">BUILD: {VERSION_VIBE}</p>
        </div>
    """, unsafe_allow_html=True)

    # 5. Core Bereich: Manifesto & Mona Lisa
    col_left, col_right = st.columns([1.2, 0.8])
    
    with col_left:
        st.subheader("Das bin ich")
        manifesto = st.text_area(
            label="Manifesto (Deine Resonanz-DNA):",
            height=350,
            placeholder="Die Vorlage. Dein qualitativer Anker. Je mehr du hier mitgibst, desto schärfer wird dein Matching-Bild. Schreib über alles was dich ausmacht - das kann und sollte auch jenseits von harten Fakten sein ;).",
            label_visibility="collapsed"
        )

    with col_right:
        # Hier injizieren wir die Mona Lisa Boxen direkt via HTML/CSS
        st.markdown("""
            <div class="visual-anchor">
                <div class="m-box">
                    <div class="m-img-container img-low">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/157px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg">
                    </div>
                    <div class="m-skeleton sk-low"></div>
                </div>
                <div class="m-box">
                    <div class="m-img-container img-high">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/157px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg">
                    </div>
                    <div class="m-skeleton sk-high"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Operative Felder (Nebeneinander)
    c1, c2, c3 = st.columns(3)
    u_name = sanitize_input(c1.text_input("Identität", placeholder="Name / Pseudonym", help="Wie du im System geführt werden willst."))
    u_loc = sanitize_input(c2.text_input("Präsenz", placeholder="Ort / Heimat", help="Dein Standort für regionales Matching."))
    u_contact = sanitize_input(c3.text_input("Signal", placeholder="Telegram Handle", help="Dein verschlüsselter Rückkanal."))

    # 7. Button & Matching Logik
    if st.button("ERZEUGE MEINE DIGITALE DNA FÜR DAS MATCHING [I AM]"):
        if u_name and manifesto and u_contact:
            st.info("AIM analysiert die Geometrie deiner Resonanz...")
            # ... DEINE BESTEHENDE EMBEDDING & DB LOGIK HIER ...
        else:
            st.warning("Bitte alle Felder ausfüllen, um eine präzise DNA zu erzeugen.")

    # 8. Footer (Transparenz Box)
    st.markdown(f"""
        <div class="footer-box">
            <h3>Beta-Status & Transparenz</h3>
            <p>Wir befinden uns aktuell im <strong>Beta-Stadium</strong>. Bitte seht es uns nach, falls noch nicht alles 100% rund läuft.<br>
            <strong>Wichtig:</strong> Notiert euch euren persönlichen Code, um euren Eintrag später anzupassen.</p>
            <p><strong>Datenschutz:</strong> Anonymität ist Key. Selbst als Admins können wir keine direkten Bezüge von Einträgen zu realen Personen herstellen.</p>
            <p>Anregungen an: <a href="mailto:marc.c.vietor@gmail.com">marc.c.vietor@gmail.com</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()