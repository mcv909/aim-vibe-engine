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
import re

# --- GANZ OBEN IN app.py (direkt nach den Imports) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'maintenance.flag')):
    st.warning("⚠️ AIM befindet sich kurzzeitig im Wartungsmodus (Backup). Bitte in 1 Min. neu laden.")
    st.stop()

def is_valid_messenger(contact):
    """Prüft auf @username oder +Nummer."""
    if not contact: return True 
    return bool(re.match(r"^(@[a-zA-Z0-9_]{3,32}|\+[0-9]{7,15})$", contact))

# --- Daten-Vorbereitung ---
user = st.session_state.get('user_data', {})
is_edit = st.session_state.get('logged_in', False)

# 1. Verbesserte Hilfsfunktion für Datenbank-Werte
def get_val(key, default):
    val = user.get(key)
    return val if val is not None else default

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

def init_db():
    """Initialisiert die vollständige AIM-Struktur (Email-First)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                identity INT, 
                search_for INT, 
                age INT,
                height INT, 
                stature_id INT, 
                coords JSONB,
                u_age_min INTEGER,
                u_age_max INTEGER,
                u_height_min INTEGER,
                u_height_max INTEGER,
                radius INTEGER DEFAULT 50,
                is_ukrainian BOOLEAN DEFAULT FALSE,
                is_email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT FALSE,
                key_hash TEXT,
                messenger_contact TEXT,
                verification_token UUID DEFAULT gen_random_uuid(),
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # WICHTIG: PRIMARY KEY auf profile_id für den ON CONFLICT Support!
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manifesto_vectors (
                profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
                manifesto_enc TEXT,
                embedding vector(1536)
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()

def save_profile_atomic(data, manifesto_raw, pub_key, v_key):
    """Speichert alle 14 Datenpunkte inklusive der Suchfilter."""
    conn = db_handler.get_connection()
    cur = conn.cursor()
    try:
        # Verschlüsselung
        user_enc = security.encrypt_data(manifesto_raw, v_key) if v_key else None
        worker_enc = security.encrypt_for_worker(manifesto_raw, pub_key)
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None

        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, coords, 
                is_ukrainian, key_hash, messenger_contact,
                u_age_min, u_age_max, u_height_min, u_height_max, radius
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, height = EXCLUDED.height, coords = EXCLUDED.coords,
                identity = EXCLUDED.identity, search_for = EXCLUDED.search_for,
                is_ukrainian = EXCLUDED.is_ukrainian,
                u_age_min = EXCLUDED.u_age_min, u_age_max = EXCLUDED.u_age_max,
                u_height_min = EXCLUDED.u_height_min, u_height_max = EXCLUDED.u_height_max,
                radius = EXCLUDED.radius, last_interaction = CURRENT_TIMESTAMP
            RETURNING id, verification_token;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], coords_json, data['is_ukrainian'],
            data.get('key_hash'), data.get('messenger_contact'),
            data['u_age_min'], data['u_age_max'], 
            data['u_height_min'], data['u_height_max'], data['radius']
        ))
        p_id, v_token = cur.fetchone()

        # Manifesto-Update
        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_user, manifesto_enc)
            VALUES (%s, %s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET 
                manifesto_user = COALESCE(EXCLUDED.manifesto_user, manifesto_vectors.manifesto_user),
                manifesto_enc = EXCLUDED.manifesto_enc;
        """, (p_id, user_enc, worker_enc))

        conn.commit()
        return v_token, "needs_verification"
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close(); conn.close()

def render_manifesto_editor(user, is_edit):
    """Stellt die vollständige DNA-Maske mit allen ursprünglichen Feldern wieder her."""
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown('<p class="centered-header" style="font-size: 1.8rem; margin-bottom: 20px;">Dein Manifesto</p>', unsafe_allow_html=True)
    
    # Manifesto-Text Handlingf
    db_text = user.get('manifesto_text', "")
    display_text = db_text if db_text else st.session_state.manifesto_buffer
    
    manifesto = st.text_area(
        "Beschreibe deinen Sound...", 
        value=display_text, 
        height=300, 
        key="main_manifesto_input", 
        label_visibility="collapsed"
    )
    st.session_state.manifesto_buffer = manifesto

    st.markdown('<p class="centered-header" style="font-size: 1.8rem; margin-top: 40px; margin-bottom: 20px;">Deine Digitale DNA</p>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Basis**")
        u_name = st.text_input("Name / Alias", value=user.get('name', ""), key="inp_name")
        u_email = st.text_input("E-Mail", value=user.get('email', ""), disabled=is_edit, key="inp_email")
        v_key = st.text_input("Vibe Key", type="password", key="inp_key") if not is_edit else None
        u_messenger = st.text_input("Messenger-Kontakt", value=user.get('messenger_contact', ""), key="inp_mess")
        # u_ukraine = st.checkbox("Ukraine Support / Herkunft", value=user.get('is_ukrainian', False), key="inp_ukr")

    with c2:
        st.markdown("**Identität**")
        u_age = st.number_input("Dein Alter", 18, 99, value=user.get('age', 25), key="inp_age")
        g_list = ["m", "w", "d"]
        g_idx = (user.get('identity', 1) - 1) if isinstance(user.get('identity'), int) else 0
        u_gender = st.selectbox("Dein Geschlecht", g_list, index=g_idx, key="inp_gender")
        u_location = st.text_input("Standort", value=user.get('location', ""), key="inp_loc") 
        u_height = st.number_input("Größe (cm)", 140, 220, value=user.get('height', 175), key="inp_height")

    with c3:
        st.markdown("**Suche**")
        s_idx = (user.get('search_for', 2) - 1) if isinstance(user.get('search_for'), int) else 1
        u_search_gender = st.selectbox("Ich suche", g_list, index=s_idx, key="inp_search_gender")
        u_age_range = st.slider("Wunsch-Alter", 18, 99, value=(user.get('u_age_min', 20), user.get('u_age_max', 40)), key="inp_age_range")
        u_radius = st.number_input("Suchradius (km)", 5, 1000, value=user.get('radius', 100), key="inp_rad")
        u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, value=(user.get('u_height_min', 160), user.get('u_height_max', 190)), key="inp_h_range")

    btn_label = "PROFIL AKTUALISIEREN" if is_edit else "DNA SICHERN & RESONANZ STARTEN"
    if st.button(btn_label, type="primary", key="save_dna_btn"):
        # Datenpaket für die atomare Speicherung
        extra_data = {
            'name': u_name, 'age': u_age, 
            'identity': g_list.index(u_gender) + 1,
            'search_for': g_list.index(u_search_gender) + 1,
            'height': u_height, 'is_ukrainian': False,
            'u_age_min': u_age_range[0], 'u_age_max': u_age_range[1],
            'u_height_min': u_target_height[0], 'u_height_max': u_target_height[1],
            'radius': u_radius, 'messenger_contact': u_messenger
        }
        handle_save_process(u_email, v_key, manifesto, u_location, is_edit, extra_data)

def render_login_form():
    """Rendert das Login-Formular und kümmert sich um die Entschlüsselung."""
    st.markdown("<h2 style='text-align: center;'>Resonanz-Zentrale</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        l_email = st.text_input("E-Mail Adresse")
        l_key = st.text_input("Vibe Key", type="password")
        if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
            user_res = db_handler.get_profile_by_email(l_email)
            if user_res and security.verify_key(l_key, user_res['key_hash']):
                st.session_state.logged_in = True
                # Manifesto aus der DB holen (Source of Truth)
                enc_manifesto = db_handler.get_user_manifesto_by_id(user_res['id'])
                if enc_manifesto:
                    # Entschlüsseln mit dem User-Key (AES) [cite: 2026-03-15]
                    user_res['manifesto_text'] = security.decrypt_data(enc_manifesto, l_key)
                st.session_state.user_data = user_res
                st.rerun()
            else:
                st.error("Zugriff verweigert. Key oder E-Mail inkorrekt.")

def handle_save_process(u_email, v_key, manifesto, u_location, is_edit, extra_data):
    """Koordiniert Geocoding, Verschlüsselung und DB-Entry."""
    if not u_email or "@" not in u_email:
        st.warning("Ohne gültige E-Mail kein Vibe-Check!")
        return

    with st.status("Verarbeite digitale DNA...") as status:
        st.write("📍 Lokalisiere Schwingungsort...")
        coords = logic.geocode_city(u_location)
        
        if coords:
            # Vorbereitung der Daten für save_profile_atomic
            user_data = {
                'email': u_email,
                'coords': coords,
                'key_hash': security.hash_key(v_key) if v_key else None,
                **extra_data
            }
            
            st.write("🔑 Webe Verschlüsselungsschichten...")
            # Wir nutzen den WORKER_PUBLIC_KEY aus der env für den Hybrid-Part [cite: 2026-03-04]
            pub_key = os.getenv("WORKER_PUBLIC_KEY")
            
            v_token, db_status = save_profile_atomic(user_data, manifesto, pub_key, v_key)
            
            if db_status == "needs_verification":
                st.write("✉ Sende Aktivierungslink...")
                if mail_logic.send_activation_mail(u_email, v_token):
                    status.update(label="DNA erfolgreich gesichert!", state="complete")
                    st.success(f"Moin! Bitte prüfe deine Mail: {u_email}")
                    st.balloons()
                else:
                    st.error("Mail-Zustellung fehlgeschlagen. Prüfe SMTP.")

def main():
    # 1. INITIALISIERUNG
    if 'menu' not in st.session_state: st.session_state.menu = "Manifesto erstellen"
    if 'manifesto_buffer' not in st.session_state: st.session_state.manifesto_buffer = ""
    
    style.apply_custom_style() 
    style.render_nav()
    
    menu = st.session_state.menu
    user = st.session_state.get('user_data', {})
    is_edit = st.session_state.get('logged_in', False)

    style.render_header()
    render_founding_dashboard()

    # ZENTRALE ROUTING-LOGIK
    # Falls wir im Editor-Modus sind (entweder neu oder eingeloggt)
    if menu == "Manifesto erstellen" or (is_edit and menu == "Login"):
        render_manifesto_editor(user, is_edit)
        
    # Falls wir nicht eingeloggt sind und den Login sehen wollen
    elif menu == "Login" and not is_edit:
        render_login_form()
        
    # Logout-Option für eingeloggte User in der Login-Ansicht
    elif menu == "Login" and is_edit:
        st.success(f"Eingeloggt als: {user.get('email')}")
        if st.button("AUS DER MATRIX AUFTAUCHEN (Logout)"):
            st.session_state.clear()
            st.rerun()

    style.render_beta_footer()


if __name__ == "__main__":
    main()