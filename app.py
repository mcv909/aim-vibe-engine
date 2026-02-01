import streamlit as st
import os
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

# Unsere Module
import security
import db_handler
import logic
import style

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

def get_embedding(text):
    """Verwandelt Text via OpenAI in einen 1536-D Vektor."""
    try:
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
    except Exception as e:
        st.error(f"DNA-Analyse fehlgeschlagen: {e}")
        return None

def main():
    style.apply_custom_style() # Das helle Design (Light Mode)
    style.render_header()
    
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
                # Wir nutzen jetzt die sauberen Funktionen aus dem db_handler
                # Das hält die app.py frei von SQL-Gedöns
                try:
                    user_count = db_handler.get_user_count()
                    match_count = db_handler.get_match_count()
                    
                    st.metric("Aktive User", user_count)
                    st.metric("Resonanzen im Feld", match_count)
                except Exception as e:
                    st.error(f"Statistik-Fehler: {e}")

            st.markdown("---")
            st.subheader("🛠️ Signal-Test (Telegram)")
            
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                test_tid = st.number_input("Telegram ID für Test-Ping", step=1, value=int(u_tid) if 'u_tid' in locals() else 0)
            with col_t2:
                st.write(" ") # Spacer
                if st.button("TEST-RESONANZ SENDEN"):
                    if test_tid > 0:
                        test_score = 0.9412 # Ein schöner fiktiver Wert
                        try:
                            # Wir nutzen direkt die notify-Funktion aus deiner logic.py
                            logic.notify_match(test_tid, 12345678, test_score)
                            st.success(f"Signal an {test_tid} wurde in die Matrix gespeist!")
                        except Exception as e:
                            st.error(f"Telegram-Fehler: {e}")
                    else:
                        st.warning("Bitte gültige Telegram ID eingeben.")

        elif admin_pw:
            security.handle_hacker()

    elif menu == "Q&A / Resonanz":
        st.switch_page("pages/qa.py")

    elif menu == "Manifesto erstellen":
        st.subheader("Deine Digitale DNA")
        
        # Anti-Frust Airbag (Session State)
        if 'manifesto_cache' not in st.session_state: st.session_state.manifesto_cache = ""

        col1, col2 = st.columns(2)
        with col1:
            u_name = st.text_input("Name / Alias", placeholder="Wie sollen wir dich nennen?")
            
            # Hilfe zur ID-Beschaffung direkt im Formular
            st.markdown(f"[🆔 Hol dir hier deine ID von AIM](https://t.me/DEIN_BOT_NAME)") 
            u_tid = st.number_input("Telegram ID", step=1, help="Klicke auf den Link oben, starte den Bot und tippe /id", value=0)
            
            v_key = st.text_input("Vibe Key", type="password", help="Wähle ein starkes Passwort. Das ist dein einziger Schlüssel!")
        with col2:
            u_contact = st.text_input("Kontakt (@Telegram)", placeholder="@handle")
            u_location = st.text_input("Standort", placeholder="Stadt...")
            u_radius = st.slider("Radius (km)", 5, 500, 50)

        manifesto = st.text_area("Dein Manifesto", value=st.session_state.manifesto_buffer if 'manifesto_buffer' in st.session_state else "", height=300)
        st.session_state.manifesto_buffer = manifesto

        u_stature = st.selectbox("Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
        u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])

        if st.button("DNA SICHERN & RESONANZ STARTEN"):
            # 1. Mudda-Sperre (Security)
            if any(security.detect_attack(f) for f in [u_name, u_contact, manifesto, v_key]):
                security.handle_hacker()
                return

            if st.button("DNA SICHERN & RESONANZ STARTEN"):
            if u_tid == 0:
                st.warning("Wir brauchen deine Telegram-ID, damit du dich später wieder einloggen kannst. Klicke oben auf den Link!")
                return
            # ... restliche Logik

            if all([u_name, u_tid, u_contact, manifesto, v_key, u_location]):
                coords = logic.get_coords(u_location)
                if not coords:
                    st.error("Ort nicht gefunden.")
                    return

                with st.spinner("Vektorisierung läuft..."):
                    real_vector = get_embedding(manifesto)
                
                if real_vector:
                    data = {
                        'telegram_id': u_tid,
                        'name_enc': security.encrypt_data(u_name, v_key),
                        'contact_enc': security.encrypt_data(u_contact, v_key),
                        'password_hash': security.hash_key(v_key),
                        'manifesto_enc': security.encrypt_data(manifesto, v_key),
                        'vector': real_vector,
                        'coords': coords,
                        'stature': u_stature,
                        'target_stature': u_target_stature,
                        'radius': u_radius,
                        'early_adopter': True
                    }

                    if db_handler.save_profile(data):
                        st.session_state.manifesto_buffer = "" # Cache leeren
                        st.success("DNA stabilisiert. Check deinen Bot!")
                        st.balloons()
                    else: st.error("Speicherfehler in Postgres.")
            else: st.warning("Eingabe unvollständig.")

    elif menu == "Login":
        st.subheader("Resonanz-Zentrale")
        
        # Login-Eingabe
        l_tid = st.number_input("Telegram ID", step=1)
        l_key = st.text_input("Vibe Key", type="password")

        if st.button("IN DIE MATRIX EINLOGGEN"):
            if security.detect_attack(l_key): 
                security.handle_hacker()
            else:
                user = db_handler.get_profile_by_telegram_id(l_tid)
                
                if user and security.verify_key(l_key, user['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    st.session_state.v_key = l_key
                    st.success(f"Resonanz stabil. Willkommen zurück!")
                else:
                    st.error("Zugriff verweigert. Falscher Key oder ID.")

        # Wenn eingeloggt: Editier-Modus anzeigen
        if st.session_state.get('logged_in'):
            st.markdown("---")
            st.subheader("🧬 Dein Manifesto tunen")
            
            # Daten entschlüsseln für die Anzeige
            current_name = security.decrypt_data(st.session_state.user_data['name_enc'], st.session_state.v_key)
            current_manifesto = security.decrypt_data(st.session_state.user_data['manifesto_enc'], st.session_state.v_key)
            current_contact = security.decrypt_data(st.session_state.user_data['contact_enc'], st.session_state.v_key)

            # Editier-Felder (vorbelegt mit aktuellen Daten)
            new_name = st.text_input("Name / Alias", value=current_name)
            new_contact = st.text_input("Kontakt (@Telegram)", value=current_contact)
            new_manifesto = st.text_area("Dein Manifesto", value=current_manifesto, height=300)
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                new_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], 
                                           index=["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"].index(st.session_state.user_data['stature']))
            with col_e2:
                new_radius = st.slider("Suchradius (km)", 5, 500, int(st.session_state.user_data['radius']))

            if st.button("ÄNDERUNGEN IN DER DB VERSIEGELN"):
                with st.spinner("Vektoren werden neu ausgerichtet..."):
                    # 1. Neue Vektoren berechnen (wichtig, falls sich der Text geändert hat!)
                    new_vector = get_embedding(new_manifesto)
                    
                    # 2. Datenpaket schnüren
                    updated_data = {
                        'telegram_id': l_tid,
                        'name_enc': security.encrypt_data(new_name, st.session_state.v_key),
                        'contact_enc': security.encrypt_data(new_contact, st.session_state.v_key),
                        'password_hash': st.session_state.user_data['password_hash'], # Bleibt gleich
                        'manifesto_enc': security.encrypt_data(new_manifesto, st.session_state.v_key),
                        'vector': new_vector,
                        'coords': st.session_state.user_data['coords'], # Bleibt vorerst gleich
                        'stature': new_stature,
                        'target_stature': st.session_state.user_data['target_stature'],
                        'radius': new_radius
                    }
                    
                    # 3. Speichern (db_handler.save_profile nutzt ON CONFLICT und macht daher automatisch ein UPDATE)
                    if db_handler.save_profile(updated_data):
                        st.success("DNA erfolgreich aktualisiert. Deine Resonanz wurde neu berechnet!")
                        st.balloons()
                    else:
                        st.error("Fehler beim Speichern in der Matrix.")

    # Der Beta-Footer am Ende jeder Seite
    style.render_beta_footer()

if __name__ == "__main__":
    main()