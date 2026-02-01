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
            u_name = st.text_input("Name / Alias", placeholder="Alias...")
            u_tid = st.number_input("Telegram ID", step=1, help="Deine ID vom Bot.")
            v_key = st.text_input("Vibe Key", type="password", help="Wichtig: Weg ist weg.")
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
        st.subheader("Resonanz-Check")
        l_tid = st.number_input("Telegram ID", step=1)
        l_key = st.text_input("Vibe Key", type="password")

        if st.button("RESONANZ PRÜFEN"):
            if security.detect_attack(l_key): security.handle_hacker()
            user = db_handler.get_profile_by_telegram_id(l_tid)
            if user and security.verify_key(l_key, user['password_hash']):
                # Name entschlüsseln
                name = security.decrypt_data(user['name_enc'], l_key)
                st.success(f"Willkommen zurück, {name}!")
            else: st.error("Zugriff verweigert.")

    # Der Beta-Footer am Ende jeder Seite
    style.render_beta_footer()

if __name__ == "__main__":
    main()