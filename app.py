import streamlit as st
import os
import json
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

# Unsere Module
import security
import db_handler
import logic
import style
import subprocess

def get_git_hash():
    try:
        # Holt die ersten 7 Zeichen der aktuellen Commit-ID
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except:
        return "Unknown"

# In der Sidebar oder im Footer anzeigen
st.sidebar.markdown(f"**System-DNA:** `{get_git_hash()}`")

# --- KONFIGURATION & PFADE ---
# Absoluter Pfad zur status.json sicherstellen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_PATH = os.path.join(BASE_DIR, 'status.json')

# 1. Page Config (muss immer zuerst kommen)
st.set_page_config(page_title="aim-vibe-test", layout="wide")

# 2. Styles laden (WICHTIG: Prüfe, ob in style.py die Klasse .aim-ribbon definiert ist!)
st.markdown(style.CSS_STÖRER, unsafe_allow_html=True)

# 3. Der Ribbon-Check (Die einzig wahre Version)
def render_ribbon():
    if not os.path.exists(STATUS_PATH):
        return
        
    try:
        with open(STATUS_PATH, 'r') as f:
            config = json.load(f)
        
        if config.get("msg_active"):
            # Wir nutzen 'aim-ribbon' statt 'störer' wegen Encodings/Umlauten
            st.markdown(f'<div class="aim-ribbon">{config.get("msg_text")}</div>', unsafe_allow_html=True)
    except Exception as e:
        # Falls es knallt, wollen wir es jetzt sehen!
        st.error(f"Ribbon-Fehler: {e}")

# 4. Ribbon ausführen
render_ribbon()

load_dotenv()

# --- INITIALISIERUNG ---
VERSION = "v0.7.6-RESILIENT-POSTGRES"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Globaler Client für Embeddings

# Datenbank-Struktur sicherstellen
if "db_initialized" not in st.session_state:
    db_handler.init_db()
    st.session_state["db_initialized"] = True

# --- UI HILFSFUNKTIONEN ---
def render_founding_dashboard():
    try:
        db = db_handler.load_db()
        current_count = len(db)
    except Exception:
        current_count = 0
        
    limit = 2000
    
    # WICHTIG: Keine Zeilenumbrüche oder Einrückungen zwischen den Tags!
    # Wir nehmen ein helleres Grau (#EEEEEE) und mehr Gewicht (500) für die Zahl.
    html_content = (
        '<div style="background-color: #111111; color: #CCCCCC; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px; border: 1px solid #333;">'
        '<p style="text-transform: uppercase; letter-spacing: 3px; font-size: 0.8rem; margin-bottom: 5px; color: #FF00FF; font-weight: 600;">Founding Member Status</p>'
        f'<div style="color: #EEEEEE !important; margin: 10px 0; font-size: 3.5rem; font-weight: 500; letter-spacing: -1px;">{current_count} / {limit}</div>'
        '<div style="margin-top: 20px; font-size: 1.0rem; font-weight: 300; border-top: 1px solid #333; padding-top: 15px; line-height: 1.5; color: #AAAAAA;">'
        'Pionier-Privileg: Dein Account bleibt <b style="color: #EEEEEE;">lebenslang beitragsfrei</b>.<br>'
        '<span style="font-size: 0.85rem; opacity: 0.7;">Gilt exklusiv für die ersten 2.000 Anmeldungen – danach wird das System kostenpflichtig.</span>'
        '</div>'
        '</div>'
    )

    st.markdown(html_content, unsafe_allow_html=True)

def main():
    style.apply_custom_style() 
    style.render_header()
    
    render_founding_dashboard()

    def main():
        st.write("DEBUG 1: Start") # Test-Ausgabe
        style.apply_custom_style() 
        
        st.write("DEBUG 2: Style geladen") # Test-Ausgabe
        style.render_header()
        
        st.write("DEBUG 3: Header fertig") # Test-Ausgabe
        render_founding_dashboard()

    menu = st.sidebar.selectbox("Navigation", ["Manifesto erstellen", "Login", "Q&A / Resonanz", "Über AIM", "Admin"])

    if menu == "Admin":
        st.subheader("Maschinenraum (Admin)")
        admin_pw = st.text_input("Admin-Passwort", type="password")
        if admin_pw == os.getenv("ADMIN_PASSWORD"):
            st.success("Willkommen im Kern, Marc.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("BATCH-MATCHING STARTEN"):
                    with st.spinner("AIM scannt die Matrix..."):
                        logic.run_batch_matching()
                    st.balloons()
            with col2:
                try:
                    user_count = db_handler.get_user_count()
                    match_count = db_handler.get_match_count()
                    st.metric("Aktive User", user_count)
                    st.metric("Resonanzen im Feld", match_count)
                except Exception as e:
                    st.error(f"Statistik-Fehler: {e}")

    elif menu == "Q&A / Resonanz":
        st.switch_page("pages/qa.py")

    elif menu == "Manifesto erstellen":
        st.subheader("Deine Digitale DNA")
        
        if 'manifesto_buffer' not in st.session_state: 
            st.session_state.manifesto_buffer = ""

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Basis")
            u_name = st.text_input("Name / Alias", placeholder="Wie sollen wir dich nennen?")
            st.markdown(f"[🆔 ID-Bot](https://t.me/aim_vibe_bot)") 
            u_tid = st.number_input("Telegram ID", step=1, value=0)
            v_key = st.text_input("Vibe Key", type="password")
            u_contact = st.text_input("Kontakt (@Telegram)", placeholder="@handle")

        with col2:
            st.markdown("### Identität")
            u_age = st.slider("Dein Alter", 18, 99, 25)
            u_gender = st.selectbox("Dein Geschlecht", ["m", "w", "d"])
            u_location = st.text_input("Standort", placeholder="Stadt...")
            u_height = st.slider("Größe (cm)", 140, 220, 175)
            u_stature = st.selectbox("Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
            
        with col3:
            st.markdown("### Suche")
            u_age_range = st.slider("Wunsch-Alter", 18, 99, (20, 40))
            u_looking_for = st.selectbox("Suche nach", ["m", "w", "d", "egal"], index=3)
            u_intent = st.selectbox("Absicht", ["partner", "friends", "both"], index=2)
            u_radius = st.slider("Suchradius (km)", 5, 500, 50)
            u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, (160, 190))
            u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])

        manifesto = st.text_area("Dein Manifesto", value=st.session_state.manifesto_buffer, height=300)
        st.session_state.manifesto_buffer = manifesto

        if st.button("DNA SICHERN & RESONANZ STARTEN", key="btn_create_final"):
            if u_tid == 0 or not u_name or not u_location or len(manifesto) < 10:
                st.warning("Pflichtfelder prüfen!")
                return

            with st.spinner("Lokalisiere & Übertrage..."):
                coords = logic.geocode_city(u_location)
                if not coords:
                    st.error("Standort nicht gefunden.")
                    return

                data = {
                    'telegram_id': u_tid,
                    'name_enc': security.encrypt_data(u_name, v_key),
                    'contact_enc': security.encrypt_data(u_contact, v_key),
                    'password_hash': security.hash_key(v_key),
                    'manifesto_enc': security.encrypt_data(manifesto, v_key),
                    'vector': None, # Initial leer, M4 übernimmt
                    'coords': coords,
                    'stature': u_stature,
                    'target_stature': ", ".join(u_target_stature),
                    'radius': u_radius,
                    'u_age': u_age, 'u_gender': u_gender, 'u_looking_for': u_looking_for,
                    'u_age_min': u_age_range[0], 'u_age_max': u_age_range[1],
                    'u_intent': u_intent, 'u_height': u_height,
                    'u_target_height_min': u_target_height[0], 'u_target_height_max': u_target_height[1],
                    'early_adopter': True
                }
                
                new_id = db_handler.save_profile(data)
                if new_id:
                    pub_key = os.getenv("WORKER_PUBLIC_KEY")
                    enc_manifesto = security.encrypt_for_worker(manifesto, pub_key)
                    if db_handler.add_to_embedding_queue(new_id, enc_manifesto):
                        st.success(f"DNA stabilisiert, {u_name}!")
                        st.info("Dein 1536-D Vibe wird lokal berechnet.")
                        st.balloons()
                    else:
                        st.error("Fehler beim Queue-Eintrag.")
                else:
                    st.error("Datenbank-Fehler beim Versiegeln.")

    elif menu == "Login":
        st.subheader("Resonanz-Zentrale")
        if not st.session_state.get('logged_in'):
            with st.form("login_form"):
                l_tid = st.number_input("Telegram ID", step=1)
                l_key = st.text_input("Vibe Key", type="password")
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    user = db_handler.get_profile_by_telegram_id(l_tid)
                    if user and security.verify_key(l_key, user['password_hash']):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.session_state.v_key = l_key
                        st.rerun()
                    else:
                        st.error("Zugriff verweigert.")

        if st.session_state.get('logged_in'):
            # Hier käme der Edit-Modus (analog zu Manifesto erstellen, nur mit UPDATE)
            st.write(f"Willkommen zurück. Dein Profil ist sicher.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

    style.render_beta_footer()

if __name__ == "__main__":
    main()