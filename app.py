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
import mail_logic

# 1. URL-Parameter abgreifen
query_params = st.query_params

if "token" in query_params:
    token = query_params["token"]
    
    # 2. Verifizierung in der DB anstoßen [cite: 2026-03-08]
    success, p_id = db_handler.verify_email_by_token(token)
    
    if success:
        st.balloons()
        st.success("### Deine E-Mail wurde erfolgreich verifiziert! 🎉")
        st.info("Dein Manifesto wird nun im 1536-dimensionalen Raum verortet."
                "Sobald die Resonanz-Berechnung abgeschlossen ist, schwingst du voll mit.")
        # Hier triggern wir optional den Worker-Hinweis
        st.query_params.clear() # Token aus der URL putzen
    else:
        st.error("Dieser Aktivierunglink ist leider ungültig oder abgelaufen.")

def get_system_dna():
    try:
        # %h = Kurz-Hash, %s = Betreffzeile der Commit-Message
        return subprocess.check_output(['git', 'log', '-1', '--format=%h | %s']).decode('utf-8').strip()
    except Exception:
        return "DNA-Sequenz korrupt"

# In der Sidebar anzeigen
st.sidebar.markdown(f"**System-DNA:** `{get_system_dna()}`")

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
    
    # --- NEU: E-MAIL VERIFIZIERUNG ÜBER URL-TOKEN --- [cite: 2026-03-08]
    if "token" in st.query_params:
        token = st.query_params["token"]
        success, p_id = db_handler.verify_email_by_token(token)
        if success:
            st.balloons()
            st.success("### E-Mail erfolgreich verifiziert! 🎉")
            st.info("Dein Manifesto wird nun im 1536-D Raum verortet. Sobald der MacAir-Worker fertig ist, bist du aktiv.")
            st.query_params.clear() # Token aus URL entfernen
    
    render_founding_dashboard()

    def main():
        st.write("DEBUG 1: Start") # Test-Ausgabe
        style.apply_custom_style() 
        
        st.write("DEBUG 2: Style geladen") # Test-Ausgabe
        style.render_header()
        
        st.write("DEBUG 3: Header fertig") # Test-Ausgabe
        render_founding_dashboard()

    # Mapping für die Statur-Logik (ID 1-5) [cite: 2026-03-08]
    STATURE_MAP = {
        "Sehr schlank": 1,
        "Schlank / Sportlich": 2,
        "Normal / Durchschnitt": 3,
        "Ein paar Kilos mehr": 4,
        "Curvy / Plus Size": 5
    }

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
        
        # 1. Das Mapping muss bekannt sein, bevor wir es nutzen [cite: 2026-03-08]
        STATURE_MAP = {
            "Sehr schlank": 1,
            "Schlank / Sportlich": 2,
            "Normal / Durchschnitt": 3,
            "Ein paar Kilos mehr": 4,
            "Curvy / Plus Size": 5
        }

        if 'manifesto_buffer' not in st.session_state: 
            st.session_state.manifesto_buffer = ""

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### Basis")
            u_name = st.text_input("Name / Alias", placeholder="Wie sollen wir dich nennen?")
            u_email = st.text_input("Deine E-Mail (für die Aktivierung)") # Wichtig für den neuen Flow! [cite: 2026-03-08]
            v_key = st.text_input("Vibe Key", type="password")
            u_messenger = st.text_input("Messenger-Kontakt (optional)", placeholder="z.B. Threema ID, Signal...")

        with col2:
            st.markdown("### Identität")
            u_age = st.slider("Dein Alter", 18, 99, 25)
            u_gender = st.selectbox("Dein Geschlecht", ["m", "w", "d"])
            u_location = st.text_input("Standort", placeholder="Stadt...")
            u_height = st.slider("Größe (cm)", 140, 220, 175)
            # HIER WAR DER FEHLER: Variable u_stature_label definiert...
            u_stature_label = st.selectbox("Deine Statur", list(STATURE_MAP.keys()))
            # ... und hier wird sie jetzt korrekt genutzt:
            u_stature_id = STATURE_MAP[u_stature_label]
            
        with col3:
            st.markdown("### Suche")
            u_age_range = st.slider("Wunsch-Alter", 18, 99, (20, 40))
            u_looking_for = st.selectbox("Suche nach", ["m", "w", "d", "egal"], index=3)
            u_intent = st.selectbox("Absicht", ["partner", "friends", "both"], index=2)
            u_radius = st.slider("Suchradius (km)", 5, 500, 50)
            u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, (160, 190))
            # Für die gesuchte Statur nutzen wir vorerst eine Liste der IDs
            u_target_statures = st.multiselect("Gesuchte Statur", list(STATURE_MAP.keys()), default=["Normal / Durchschnitt"])

        # Manifesto Feld (Jetzt wieder sichtbar, da der Code darüber nicht mehr crasht)
        manifesto = st.text_area("Dein Manifesto", value=st.session_state.manifesto_buffer, height=300)
        st.session_state.manifesto_buffer = manifesto

        if st.button("DNA SICHERN & RESONANZ STARTEN", key="btn_create_final"):
            # Validierung
            if not u_email or "@" not in u_email:
                st.warning("Ohne gültige E-Mail kein Vibe-Check!")
                return
            
            with st.spinner("Lokalisiere & Übertrage..."):
                coords = logic.geocode_city(u_location) #
                if not coords:
                    st.error("Standort nicht gefunden.")
                    return

                # Daten-Paket für den db_handler
                user_data = {
                    'email': u_email,
                    'identity': 1, # Platzhalter, später Mapping
                    'search_for': 2, 
                    'age': u_age, 
                    'height': u_height,
                    'stature_id': u_stature_id,
                    'coords': coords,
                    'is_ukrainian': st.session_state.get('is_ukrainian', False),
                    'messenger_contact': u_messenger,
                    'key_hash': security.hash_key(v_key),
                    'u_age_min': u_age_range[0],
                    'u_age_max': u_age_range[1],
                    'u_height_min': u_target_height[0],
                    'u_height_max': u_target_height[1],
                    'radius': u_radius
                }
                
                pub_key = os.getenv("WORKER_PUBLIC_KEY")
                # Aufruf der neuen atomaren Funktion
                v_token, status = db_handler.save_profile_atomic(user_data, manifesto, pub_key)

                if status == "needs_verification":
                    if mail_logic.send_activation_mail(u_email, v_token):
                        st.success(f"DNA stabilisiert! Bitte prüfe dein Postfach ({u_email}).")
                        st.balloons()
                    else:
                        st.error("Mail-Versand fehlgeschlagen. Google-Setup prüfen!")

                # --- DER FINALE VERSIGELUNGS-BLOCK ---
                # Wir entpacken die Rückgabe: ID und den spezifischen Status
                # Wir laden den Key für die hybride Verschlüsselung
                pub_key = os.getenv("WORKER_PUBLIC_KEY")
                v_token, status = db_handler.save_profile_atomic(user_data, manifesto, pub_key)

            
                if status == "needs_verification":
                    # Mail-Versand via Google Workspace SMTP [cite: 2026-03-08]
                    if mail_logic.send_activation_mail(u_email, v_token):
                        st.success(f"DNA stabilisiert! Bitte prüfe dein Postfach: {u_email}")
                    else:
                        st.error("Mail-Versand fehlgeschlagen. Bitte Admin kontaktieren.")

    elif menu == "Login":
        st.subheader("Resonanz-Zentrale")
        if not st.session_state.get('logged_in'):
            with st.form("login_form"):
                l_email = st.text_input("E-Mail Adresse") # Wechsel von TID auf Email [cite: 2026-03-08]
                l_key = st.text_input("Vibe Key", type="password")
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    user = db_handler.get_profile_by_email(l_email) # Neue Funktion [cite: 2026-03-08]
                    if user and security.verify_key(l_key, user['key_hash']):
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