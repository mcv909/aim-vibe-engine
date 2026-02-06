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
        
        if 'manifesto_buffer' not in st.session_state: 
            st.session_state.manifesto_buffer = ""

        # Die 3-Spalten-Architektur für maximale Übersicht
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Basis")
            u_name = st.text_input("Name / Alias", placeholder="Wie sollen wir dich nennen?")
            st.markdown(f"[🆔 ID-Bot](https://t.me/aim_vibe_bot)") 
            u_tid = st.number_input("Telegram ID", step=1, value=0)
            v_key = st.text_input("Vibe Key", type="password", help="Dein Passwort zur Verschlüsselung.")
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
            u_radius = st.slider("Suchradius (km)", 5, 500, 50) # Nur noch EINMAL hier

            # DER VERMISSTE SLIDER:
            u_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, (160, 190))

            u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])

        manifesto = st.text_area("Dein Manifesto (Der qualitative Anker)", value=st.session_state.manifesto_buffer, height=300)
        st.session_state.manifesto_buffer = manifesto

        if st.button("DNA SICHERN & RESONANZ STARTEN", key="btn_create_final"):
            # Validierung & Geocoding
            if u_tid == 0 or not u_name or not u_location or len(manifesto) < 10:
                st.warning("Pflichtfelder prüfen: Name, ID, Standort und Manifesto (min. 10 Zeichen)!")
                return

            with st.spinner("Lokalisiere..."):
                coords = logic.geocode_city(u_location)
                if not coords:
                    st.error("Standort nicht gefunden.")
                    return

            # Vektorisierung & Speichern
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
                    'stature': ", ".join(u_stature), # LISTE ZU STRING WANDELN!
                    'target_stature': ", ".join(u_target_stature), # LISTE ZU STRING WANDELN!
                    'radius': u_radius,
                    'u_age': u_age,
                    'u_gender': u_gender,
                    'u_looking_for': u_looking_for,
                    'u_age_min': u_age_range[0],
                    'u_age_max': u_age_range[1],
                    'u_intent': u_intent,
                    'u_height': u_height,
                    'u_target_height_min': u_target_height[0], # Untergrenze vom Slider
                    'u_target_height_max': u_target_height[1], # Obergrenze vom Slider
                    'early_adopter': True
                }
                
                if db_handler.save_profile(data):
                    st.success(f"DNA stabilisiert, {u_name}!")
                    st.balloons()
                else:
                        st.error("Datenbank-Fehler beim Versiegeln der DNA.")
            else:
                st.error("KI-Fehler: Konnte keine Vektoren aus deinem Text extrahieren.")

    elif menu == "Login":
        st.subheader("Resonanz-Zentrale")
        
        # 1. Login-Logik (Nur anzeigen, wenn NICHT eingeloggt)
        if not st.session_state.get('logged_in'):
            with st.form("login_form"):
                l_tid = st.number_input("Telegram ID", step=1)
                l_key = st.text_input("Vibe Key", type="password")
                
                if st.form_submit_button("IN DIE MATRIX EINLOGGEN"):
                    if security.detect_attack(l_key): 
                        security.handle_hacker()
                    else:
                        user = db_handler.get_profile_by_telegram_id(l_tid)
                        if user and security.verify_key(l_key, user['password_hash']):
                            st.session_state.logged_in = True
                            st.session_state.user_data = user
                            st.session_state.v_key = l_key
                            st.success("Resonanz stabil. Willkommen zurück!")
                            st.rerun()
                        else:
                            st.error("Zugriff verweigert. Falscher Key oder ID.")

        # 2. Editier-Modus (Nur anzeigen, wenn EINGELOGGT)
        if st.session_state.get('logged_in'):
            # Daten für diesen Durchlauf entschlüsseln
            try:
                current_name = security.decrypt_data(st.session_state.user_data['name_enc'], st.session_state.v_key)
                current_manifesto = security.decrypt_data(st.session_state.user_data['manifesto_enc'], st.session_state.v_key)
                current_contact = security.decrypt_data(st.session_state.user_data['contact_enc'], st.session_state.v_key)
            except Exception:
                st.error("Fehler beim Entschlüsseln der DNA.")
                return

            st.markdown("---")
            st.subheader(f"🧬 Manifesto von {current_name} tunen")
            
            with st.form("edit_profile_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_name = st.text_input("Name / Alias", value=current_name)
                    new_contact = st.text_input("Kontakt (@Telegram)", value=current_contact)
                    # Sicherer Zugriff auf neue Spalten
                    raw_h = st.session_state.user_data.get('u_height')
                    old_h = int(raw_h) if raw_h is not None else 175
                    new_height = st.slider("Deine Größe (cm)", 140, 220, old_h)
                
                with col_e2:
                    new_stature = st.selectbox("Deine Statur", 
                        ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], 
                        index=["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"].index(st.session_state.user_data['stature']))
                    
                    new_radius = st.slider("Suchradius (km)", 5, 500, int(st.session_state.user_data['radius']))
                    
                    raw_min = st.session_state.user_data.get('u_target_height_min')
                    raw_max = st.session_state.user_data.get('u_target_height_max')
                    old_min = int(raw_min) if raw_min is not None else 160
                    old_max = int(raw_max) if raw_max is not None else 190
                    new_target_height = st.slider("Gesuchte Größe (cm)", 140, 220, (old_min, old_max))

                current_targets = st.session_state.user_data.get('target_stature', ["durchschnittlich"])
                new_target_stature = st.multiselect("Gesuchte Statur", 
                    ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"],
                    default=current_targets)

                new_manifesto = st.text_area("Dein Manifesto", value=current_manifesto, height=300)
                
                if st.form_submit_button("ÄNDERUNGEN IN DER DB VERSIEGELN"):
                    new_vector = get_embedding(new_manifesto)
                    updated_data = {
                        'telegram_id': st.session_state.user_data['telegram_id'],
                        'name_enc': security.encrypt_data(new_name, st.session_state.v_key),
                        'contact_enc': security.encrypt_data(new_contact, st.session_state.v_key),
                        'password_hash': st.session_state.user_data['password_hash'],
                        'manifesto_enc': security.encrypt_data(new_manifesto, st.session_state.v_key),
                        'vector': new_vector,
                        'coords': st.session_state.user_data['coords'],
                        'stature': new_stature,
                        'target_stature': new_target_stature,
                        'radius': new_radius,
                        'u_height': new_height,
                        'u_target_height_min': new_target_height[0],
                        'u_target_height_max': new_target_height[1]
                    }
                    if db_handler.save_profile(updated_data):
                        st.session_state.user_data.update(updated_data)
                        st.success("DNA erfolgreich aktualisiert!")
                        st.rerun()

            # 3. FEEDBACK (Außerhalb des Edit-Forms)
            st.markdown("---")
            st.subheader("⭐ Wie resonant ist AIM?")
            with st.form("feedback_form"):
                rating = st.select_slider("Bewertung", options=[1, 2, 3, 4, 5], value=3)
                comment = st.text_area("Anmerkungen")
                if st.form_submit_button("Feedback senden"):
                    db_handler.save_feedback(st.session_state.user_data['id'], rating, comment)
                    st.success("Danke für deine Resonanz!")

            # 4. GEFAHRENZONE (Absolut sicher getrennt)
            st.markdown("---")
            with st.expander("🚨 Gefahrenzone"):
                st.write("Vorsicht: Das Löschen deiner DNA ist irreversibel.")
                if st.button("PROFIL UNWIDERRUFLICH LÖSCHEN", type="primary", key="final_del_btn"):
                    if db_handler.delete_profile(st.session_state.user_data['telegram_id']):
                        st.session_state.clear()
                        st.rerun()                        

    # Der Beta-Footer am Ende jeder Seite
    style.render_beta_footer()

if __name__ == "__main__":
    main()