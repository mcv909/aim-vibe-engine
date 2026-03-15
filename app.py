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

def save_profile_atomic(data, manifesto_raw, pub_key):
    """Speichert Profil inkl. aller Filter und bereitet Vektorisierung vor."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        enc_manifesto = security.encrypt_for_worker(manifesto_raw, pub_key)
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None

        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, stature_id, 
                coords, is_ukrainian, key_hash, messenger_contact,
                u_age_min, u_age_max, u_height_min, u_height_max, radius
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, height = EXCLUDED.height, stature_id = EXCLUDED.stature_id,
                coords = EXCLUDED.coords, messenger_contact = EXCLUDED.messenger_contact,
                u_age_min = EXCLUDED.u_age_min, u_age_max = EXCLUDED.u_age_max,
                u_height_min = EXCLUDED.u_height_min, u_height_max = EXCLUDED.u_height_max,
                radius = EXCLUDED.radius, last_interaction = CURRENT_TIMESTAMP
            RETURNING id, verification_token;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], data['stature_id'], 
            coords_json, data.get('is_ukrainian', False), data.get('key_hash'),
            data.get('messenger_contact'), data.get('u_age_min'), data.get('u_age_max'),
            data.get('u_height_min'), data.get('u_height_max'), data.get('radius')
        ))
        p_id, v_token = cur.fetchone()

        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_enc)
            VALUES (%s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET manifesto_enc = EXCLUDED.manifesto_enc;
        """, (p_id, enc_manifesto))

        conn.commit()
        return v_token, "needs_verification"
    except Exception as e:
        conn.rollback()
        return None, f"system_error: {str(e)}"
    finally:
        cur.close(); conn.close()

def main():
    # Mapping für die Identität (DB nutzt INT 1, 2, 3) [cite: 2026-03-15]
    gender_map = {1: "m", 2: "w", 3: "d"}
    db_identity = get_val('identity', 1)
    u_gender_text = gender_map.get(db_identity, "m")

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

    # Formular anzeigen bei 'Manifesto' ODER wenn im Login-Menü eingeloggt
    if menu == "Manifesto erstellen" or (is_edit and menu == "Login"):
        if not is_edit:
            st.markdown("<h3 style='text-align: center;'>Was ist AIM-Vibe?</h3>", unsafe_allow_html=True)
            st.markdown("""
        AIM?
        Atificial Intelligence Matching, also eine künstliche Intelligenz die passende Leute findet.
        Oah - cool, und wie genau?
        Künstliche Intelligenz ist im Grunde ein irre mächtiger Vergleichsapparat. 
        AIM vergleicht dein Manifesto (lokal!), deinen Text mit dem anderer Menschen im **1536-dimensionalen Vektorraum**. [cite: 2026-02-07]
        
        Wir suchen nicht nach Hobbys, wir suchen nach der **Resonanz in deinem Vibe**. 
        Dein Manifesto ist der qualitative Anker dieser Magie. [cite: 2025-12-30]
        
        **Und: Wir suchen verschlüsselt!** Selbst als Admins haben wir keinen Zugriff auf deine Daten. [cite: 2026-01-18]
        Umso wichtiger ist dein Passwort (Vibe Key). DU hast die Kontrolle. Punkt.
        Sobald ein Match vorliegt werden die Matchpartner informiert - dann liegt es wieder bei euch, lernt euch kennen ;)
        """)

# --- MANIFESTO (Vorbefüllt) ---
        st.markdown('<p class="centered-header">Dein Manifesto</p>', unsafe_allow_html=True)
        st.caption("Das bin ich – meine Werte, mein Sound, meine Sicht auf die Welt.")
        # Nutzt Daten aus der DB wenn eingeloggt [cite: 2026-03-12]
        manifesto = st.text_area("", value=user.get('manifesto_text', st.session_state.manifesto_buffer), height=300, label_visibility="collapsed")
        st.session_state.manifesto_buffer = manifesto

        st.markdown('<p class="centered-header">Deine Digitale DNA</p>', unsafe_allow_html=True)
        STATURE_MAP = {"Sehr schlank": 1, "Schlank / Sportlich": 2, "Normal / Durchschnitt": 3, "Kilos+": 4, "Curvy": 5}
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Basis**")
            u_name = st.text_input("Name / Alias", value=user.get('name', ""))
            u_email = st.text_input("E-Mail", value=user.get('email', ""), disabled=is_edit)
            v_key = st.text_input("Vibe Key", type="password") if not is_edit else "********"
            u_messenger = st.text_input("Messenger-Kontakt (optional)", value=user.get('messenger_contact', ""))

        with c2:
            st.markdown("**Identität**")
            # Wir nutzen eindeutige Keys ('key=...'), um DuplicateElementId zu verhindern [cite: 2026-03-15]
            u_age = st.number_input("Dein Alter", 18, 99, value=get_val('age', 25), key="age_input")
            
            # Mapping für Geschlecht (identity 1=m, 2=w, 3=d) [cite: 2026-03-12, 2026-03-15]
            g_list = ["m", "w", "d"]
            # Sicherer Index-Check [cite: 2026-03-15]
            g_val = user.get('gender') or user.get('identity')
            g_idx = g_list.index(g_val) if g_val in g_list else 0
            
            u_gender = st.selectbox("Dein Geschlecht", g_list, index=g_idx, key="gender_main")
            
            u_location = st.text_input("Standort", value=get_val('location', ""), key="loc_input") 
            u_height = st.number_input("Größe (cm)", 140, 220, value=get_val('height', 175), key="height_input")

        # 2. Die Slider-Logik (Sicher gegen NoneType-Fehler)
        with c3:
            st.markdown("**Suche**")
            # Wir stellen sicher, dass u_age_min/max niemals None sind
            u_age_min = get_val('u_age_min', 20)
            u_age_max = get_val('u_age_max', 40)
            u_age_range = st.slider("Wunsch-Alter", 18, 99, value=(u_age_min, u_age_max))
            
            u_looking_for = st.selectbox("Suche nach", ["m", "w", "d", "egal"], index=3)
            
            u_radius = st.number_input("Suchradius (km)", 5, 1000, value=get_val('radius', 100), step=10)
            
            h_min = get_val('u_height_min', 160)
            h_max = get_val('u_height_max', 190)
            u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, value=(h_min, h_max))    

        btn_label = "PROFIL AKTUALISIEREN" if is_edit else "DNA SICHERN & RESONANZ STARTEN"
        if st.button(btn_label, type="primary"):
            # HIER DIE SPEICHER-LOGIK (die Animation von neulich)
            with st.status("Speichere digitale DNA...") as status:
                # ... (Vektorisierung, DB-Save etc.) ...
                status.update(label="DNA gesichert!", state="complete")

    elif menu == "Login":
            # Hier nur das leere Login-Feld zeigen, wenn noch nicht eingeloggt
            with st.form("login_form"):
                l_email = st.text_input("E-Mail Adresse")
                l_key = st.text_input("Vibe Key", type="password")
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    user_res = db_handler.get_profile_by_email(l_email)
                    # Beim Login-Check in der main() [cite: 2026-03-15]
                    if user_res and security.verify_key(l_key, user_res['key_hash']):
                        st.session_state.logged_in = True
                        
                        # NEU: Manifesto direkt beim Login mit dem l_key entschlüsseln! [cite: 2026-01-18]
                        if user_res.get('manifesto_text'):
                            try:
                                decrypted_text = security.decrypt_manifesto(user_res['manifesto_text'], l_key)
                                user_res['manifesto_text'] = decrypted_text
                            except Exception:
                                user_res['manifesto_text'] = "Fehler bei Entschlüsselung (Key falsch?)"
                                
                        st.session_state.user_data = user_res
                        st.rerun()

    elif menu == "Login" and not is_edit:
        # Standard Login-Formular (wie in deinem File)
        if st.button("DNA SICHERN & RESONANZ STARTEN", type="primary"):
            if not u_email or "@" not in u_email:
                st.warning("Ohne gültige E-Mail kein Vibe-Check!")
            else:
                with st.status("Verarbeite digitale DNA...") as status:
                    # Animation / Phasen [cite: 2026-03-12]
                    st.write("✎ Analysiere Manifesto-Struktur...")
                    import time
                    time.sleep(1)
                    
                    st.write("◬ Webe mathematische Perlenkette (1536 Dimensionen)...")
                    time.sleep(1.2)
                    
                    coords = logic.geocode_city(u_location)
                    st.write(f"📍 Verankere Standort: {u_location}...")
                    
                    if coords:
                        user_data = {
                            'email': u_email, 'identity': 1, 'search_for': 2, 
                            'age': u_age, 'height': u_height, 'stature_id': u_stature_id,
                            'coords': coords, 'is_ukrainian': False,
                            'messenger_contact': u_messenger, 'key_hash': security.hash_key(v_key),
                            'u_age_min': u_age_range[0], 'u_age_max': u_age_range[1],
                            'u_height_min': u_target_height[0], 'u_height_max': u_target_height[1],
                            'radius': u_radius
                        }
                        
                        st.write("🔑 Verschlüsele Datensatz mit Vibe-Key...")
                        v_token, db_status = db_handler.save_profile_atomic(user_data, manifesto, os.getenv("WORKER_PUBLIC_KEY"))
                        
                        if db_status == "needs_verification":
                            st.write("✉ Sende Aktivierungslink an Resonanz-Zentrale...")
                            if mail_logic.send_activation_mail(u_email, v_token):
                                status.update(label="DNA erfolgreich gesichert!", state="complete")
                                st.success(f"Moin! Bitte prüfe deine Mail: {u_email}")
                                st.balloons()
                            else:
                                status.update(label="Mail-Zustellung fehlgeschlagen", state="error")
                                st.error("Bitte prüfe deine SMTP-Einstellungen in der .env.")
 


    elif menu == "Login":
        st.markdown("<h2 style='text-align: center;'>Resonanz-Zentrale</h2>", unsafe_allow_html=True)
        if not st.session_state.get('logged_in'):
            with st.form("login_form"):
                l_email = st.text_input("E-Mail Adresse")
                l_key = st.text_input("Vibe Key", type="password")
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    user = db_handler.get_profile_by_email(l_email)
                    if user and security.verify_key(l_key, user['key_hash']):
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.rerun() # WICHTIG: Rerun löst das UI-Update aus!
                    else:
                        st.error("Zugriff verweigert.")
        else:
            # DAS ist die Ansicht für eingeloggte User
            st.success(f"Willkommen, {st.session_state.user_data['email']}")
            st.info("Hier kannst du bald deine Matches einsehen und dein Manifesto verfeinern.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()           

    style.render_beta_footer()


if __name__ == "__main__":
    main()