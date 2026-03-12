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
    # --- 1. INITIALISIERUNG (Ganz wichtig!) ---
    if 'menu' not in st.session_state:
        st.session_state.menu = "Manifesto erstellen"
    
    # Hier fixen wir deinen AttributeError:
    if 'manifesto_buffer' not in st.session_state:
        st.session_state.manifesto_buffer = ""

    # --- 2. STYLES LADEN ---
    style.apply_custom_style() 
    # In app.py UND about.py direkt nach style.apply_custom_style()
    style.render_nav()
    
    # --- TOP-NAVIGATION (Reduziert) ---
    # nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    # if nav_cols[0].button("📝 Manifesto erstellen"): st.session_state.menu = "Manifesto erstellen"
    # if nav_cols[1].button("🔑 Login"): st.session_state.menu = "Login"
    # if nav_cols[2].button("🎯 Resonanz"): st.session_state.menu = "QA"
    # if nav_cols[3].button("ℹ️ Über AIM"): 
    #     st.session_state.menu = "About"
    #     # Wir springen direkt zur neuen Seite
    #     st.switch_page("pages/about.py")
    # if nav_cols[4].button("⚙️ Admin"): st.session_state.menu = "Admin"

    menu = st.session_state.menu
    style.render_header()
    render_founding_dashboard()

    if menu == "Manifesto erstellen":
        # --- ERKLÄRUNGS-BLOCK ---
        st.markdown("<h3 style='text-align: center;'>Was ist AIM-Vibe?</h3>", unsafe_allow_html=True)
        st.markdown("""
        **<u>A</u>IM? <u>A</u>rtificial <u>I</u>ntelligence <u>M</u>atching**, also eine künstliche Intelligenz die passende Leute findet.
        Oah - cool, und wie genau? Künstliche Intelligenz ist im Grunde ein irre mächtiger Vergleichsapparat. 
        AIM vergleicht dein Manifesto (lokal!), deinen Text mit dem anderer Menschen im **1536-dimensionalen Vektorraum**. [cite: 2026-02-07]
        
        Wir suchen nicht nach Hobbys, wir suchen nach der **Resonanz in deinem Vibe**. 
        Dein Manifesto ist der qualitative Anker dieser Magie. [cite: 2025-12-30]
        
        **Und: Wir suchen verschlüsselt!** Selbst als Admins haben wir keinen Zugriff auf deine Daten. [cite: 2026-01-18]
        Umso wichtiger ist dein Passwort (Vibe Key). DU hast die Kontrolle. Punkt.
        Sobald ein Match vorliegt werden die Matchpartner informiert - dann liegt es wieder bei euch, lernt euch kennen ;)
        """)

        # --- MANIFESTO (Zentriert & Ohne Nummer) ---
        st.markdown('<p class="centered-header">Dein Manifesto</p>', unsafe_allow_html=True)
        manifesto = st.text_area("", value=st.session_state.manifesto_buffer, height=300, label_visibility="collapsed")
        st.session_state.manifesto_buffer = manifesto

        # --- DIGITALE DNA (Zentriert & Ohne Nummer) ---
        st.markdown('<p class="centered-header">Deine Digitale DNA</p>', unsafe_allow_html=True)
        
        STATURE_MAP = {"Sehr schlank": 1, "Schlank / Sportlich": 2, "Normal / Durchschnitt": 3, "Kilos+": 4, "Curvy": 5}
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Basis**")
            u_name = st.text_input("Name / Alias")
            u_email = st.text_input("E-Mail (für Aktivierung)")
            v_key = st.text_input("Vibe Key", type="password")
            u_messenger = st.text_input("Messenger-Kontakt (optional)")

        with c2:
            st.markdown("**Identität**")
            u_age = st.number_input("Dein Alter", 18, 99, 25)
            u_gender = st.selectbox("Dein Geschlecht", ["m", "w", "d"])
            # LEERZEILE FÜR ALIGNMENT (Schiebt Standort auf Höhe von Suchradius) [cite: 2026-03-11]
            st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True) 
            u_location = st.text_input("Standort") 
            u_height = st.number_input("Größe (cm)", 140, 220, 175)
            u_st_label = st.selectbox("Deine Statur", list(STATURE_MAP.keys()))
            u_stature_id = STATURE_MAP[u_st_label]

        with c3:
            st.markdown("**Suche**")
            u_age_range = st.slider("Wunsch-Alter", 18, 99, (20, 40))
            u_looking_for = st.selectbox("Suche nach", ["m", "w", "d", "egal"], index=3)
            # Alignment: Suchradius korrespondiert mit Standort
            u_radius = st.slider("Suchradius (km)", 5, 500, 50)
            # Alignment: Gesuchte Größe korrespondiert mit Größe
            u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, (160, 190))
            u_target_statures = st.multiselect("Gesuchte Statur", list(STATURE_MAP.keys()), default=["Normal / Durchschnitt"])

        if st.button("DNA SICHERN & RESONANZ STARTEN", type="primary"):
            if not u_email or "@" not in u_email:
                st.warning("Ohne gültige E-Mail kein Vibe-Check!")
            else:
                with st.status("Verarbeite digitale DNA...") as status:
                    coords = logic.geocode_city(u_location)
                    if coords:
                        user_data = {
                            'email': u_email, 'identity': 1, 'search_for': 2, 
                            'age': u_age, 'height': u_height, 'stature_id': u_stature_id,
                            'coords': coords, 'is_ukrainian': False, # DEAKTIVIERT [cite: 2026-03-11]
                            'messenger_contact': u_messenger, 'key_hash': security.hash_key(v_key),
                            'u_age_min': u_age_range[0], 'u_age_max': u_age_range[1],
                            'u_height_min': u_target_height[0], 'u_height_max': u_target_height[1],
                            'radius': u_radius
                        }
                        v_token, db_status = db_handler.save_profile_atomic(user_data, manifesto, os.getenv("WORKER_PUBLIC_KEY"))
                        if db_status == "needs_verification":
                            if mail_logic.send_activation_mail(u_email, v_token): # [cite: 2026-03-08]
                                status.update(label="DNA gesichert!", state="complete")
                                st.success(f"Moin! Bitte prüfe deine Mail: {u_email}")
                                st.balloons()
                            else:
                                status.update(label="Mail-Fehler!", state="error")
                                st.error("Konnte Aktivierungs-Mail nicht senden. Google-Setup prüfen.")
                        else:
                            status.update(label="Datenbank-Fehler!", state="error")
                            st.error(f"Fehler beim Speichern: {db_status}")
 
    elif menu == "Login":
        st.subheader("Resonanz-Zentrale")
        if not st.session_state.get('logged_in'):
            with st.form("login_form"):
                l_email = st.text_input("E-Mail Adresse") # Pivot auf Email [cite: 2026-03-08]
                l_key = st.text_input("Vibe Key", type="password")
                
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    # Wir holen das Profil über die neue E-Mail-Funktion [cite: 2026-03-08]
                    user = db_handler.get_profile_by_email(l_email)
                    
                    if user and security.verify_key(l_key, user['key_hash']): # [cite: 2026-01-18]
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.session_state.v_key = l_key
                        st.success("Login erfolgreich!")
                        st.rerun()
                    else:
                        st.error("Zugriff verweigert. E-Mail oder Key nicht korrekt.")

        if st.session_state.get('logged_in'):
            # Hier käme der Edit-Modus (analog zu Manifesto erstellen, nur mit UPDATE)
            st.write(f"Willkommen zurück. Dein Profil ist sicher.")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

    style.render_beta_footer()

if __name__ == "__main__":
    main()