import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Unsere neuen Module
import security
import db_handler
import logic
import style

# --- INITIALISIERUNG ---
load_dotenv()
VERSION = "v0.7.6-Verbesserungen: DB, SEC und Änderung Batchlauf etc-TST"

# Datenbank-Struktur sicherstellen (Einmalig/Idempotent)
if "db_initialized" not in st.session_state:
    db_handler.init_db()
    st.session_state["db_initialized"] = True

# --- UI HILFSFUNKTIONEN ---
def render_founding_dashboard():
    """Zeigt den exklusiven Status der ersten 2000 Plätze."""
    # Hier ziehen wir die echte Anzahl aus der DB (später Count Query)
    current_count = 42 # Beispielwert für TST
    limit = 2000
    remaining = limit - current_count
    
    st.markdown(f"""
        <div style="text-align: center; border: 1px solid #1B263B; padding: 20px; margin-bottom: 30px;">
            <p style="text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem; margin: 0;">Founding Member Status</p>
            <h2 style="font-size: 2rem; margin: 10px 0;">{remaining} / {limit}</h2>
            <p style="font-size: 0.8rem; opacity: 0.6;">Sichere dir lebenslange Resonanz ohne Gebühren.</p>
        </div>
    """, unsafe_allow_html=True)

def get_embedding(text):
    """Verwandelt Text in einen mathematischen Vektor (1536 Dimensionen)."""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"OpenAI Fehler: {e}")
        return None

def main():
    style.apply_custom_style() # Das hart cleane Design
    
    st.title("[ i am ]")
    render_founding_dashboard()

    menu = st.sidebar.selectbox("Matrix-Navigation", ["Manifesto erstellen", "Login", "Über AIM"])

    if menu == "Manifesto erstellen":
        st.subheader("Deine Digitale DNA")
        
        col1, col2 = st.columns(2)
        with col1:
            u_name = st.text_input("Name / Alias", placeholder="Wie soll ich dich nennen?")
            u_tid = st.number_input("Telegram ID", step=1, help="Deine ID vom Bot.")
            v_key = st.text_input("Vibe Key (Dein Passwort)", type="password", help="Wichtig: Backup-Pflicht! Weg ist weg.")
            
        with col2:
            u_contact = st.text_input("Kontakt (@Telegram)", placeholder="@handle")
            u_location = st.text_input("Dein Standort", placeholder="Stadt, Land")
            u_radius = st.slider("Radius (km)", 5, 500, 50)

        manifesto = st.text_area("Dein Manifesto", height=300, placeholder="Wer bist du wirklich? Was schwingt in dir?")
        
        u_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
        u_target_stature = st.multiselect("Gesuchte Resonanz-Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])

        if st.button("DNA SICHERN & RESONANZ STARTEN"):
            if all([u_name, u_tid, u_contact, manifesto, v_key, u_location]):
                # 1. Mudda-Protokoll (Security Check)
                if any(security.detect_attack(f) for f in [u_name, u_contact, manifesto, v_key]):
                    security.handle_hacker()
                
                # 2. Geocoding
                coords = logic.get_coords(u_location)
                if not coords:
                    st.error("Ort nicht gefunden. Check die Schreibweise.")
                    return

                # 3. Encryption & Hashing (Zero-Knowledge)
                enc_manifesto = security.encrypt_data(manifesto, v_key)
                enc_name = security.encrypt_data(u_name, v_key) # Auch Name verschlüsselt
                enc_contact = security.encrypt_data(u_contact, v_key)
                pw_hash = security.hash_key(v_key)
                
                # 4. Dummy-Vektor für TST (später OpenAI Embedding)
                with st.spinner("AIM analysiert die Schwingungen deines Manifestos..."):
                    real_vector = get_embedding(manifesto)
                
                if not real_vector:
                    st.error("Konnte keine DNA-Analyse durchführen. API-Key in .env?")
                    return

                data = {
                    'telegram_id': u_tid, 'name_enc': enc_name, 'contact_enc': enc_contact,
                    'password_hash': pw_hash, 'manifesto_enc': enc_manifesto, 'vector': real_vector,
                    'coords': coords, 'stature': u_stature, 'target_stature': u_target_stature,
                    'radius': u_radius, 'early_adopter': True
                }

                if db_handler.save_profile(data):
                    st.success("DNA erfolgreich in der Matrix stabilisiert. Dein Batch-Matching läuft an.")
                else:
                    st.error("Fehler beim Speichern. Matrix-Kollision?")
            else:
                st.warning("Eingabe unvollständig.")

    elif menu == "Login":
        st.subheader("Resonanz-Check")
        l_tid = st.number_input("Telegram ID", step=1)
        l_key = st.text_input("Vibe Key", type="password")

        if st.button("RESONANZ PRÜFEN"):
            if security.detect_attack(l_key): security.handle_hacker()
            
            user = db_handler.get_profile_by_telegram_id(l_tid)
            if user and security.verify_key(l_key, user['password_hash']):
                st.success(f"Willkommen zurück, {security.decrypt_data(user['name_enc'], l_key)}!")
                # Hier können wir später Matches anzeigen
            else:
                st.error("Zugriff verweigert. Key oder ID inkorrekt.")

if __name__ == "__main__":
    main() 