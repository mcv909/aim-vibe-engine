import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# UNSERE MODULE
from security import encrypt_data, decrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import calculate_similarity, is_gender_match, send_telegram_msg
from style import set_page_style, render_header # Importiere das neue Style-Modul

# 1. Setup & Konfiguration
load_dotenv()
VERSION = "v0.6.0-LOGIN-TST"

def main():
    st.set_page_config(page_title="I AM | AIM (Test)", layout="wide", initial_sidebar_state="collapsed")
    set_page_style() # Setze das globale CSS
    
    # UI Branding mit Mona Lisa Header
    st.title(f"🧬 [i am] | {VERSION}")
    render_header()

    # 2. Zentraler Einstieg: Der Vibe Key als Weiche
    st.markdown("### 🔑 Dein Zugang")
    vibe_key = st.text_input("Gib deinen Vibe Key ein", type="password", help="Dies ist dein Passwort zum Einloggen oder Registrieren.")
    
    if vibe_key:
        v_hash = hash_key(vibe_key)
        db = load_db()
        
        # Prüfen, ob ein User mit diesem Key-Hash existiert
        user_profile = next((item for item in db if item["key_hash"] == v_hash), None)
        
        if user_profile:
            # --- MODUS A: LOGIN (Profil bekannt) ---
            st.success(f"Willkommen zurück, **{user_profile['name']}**!")
            
            with st.expander("Dein Profil ansehen", expanded=False):
                st.write(f"**Geschlecht:** {user_profile['gender'].upper()}")
                st.write(f"**Sucht:** {user_profile['pref'].upper()}")
                # Kontakt ist verschlüsselt gespeichert!
                st.write(f"**Kontakt (verschlüsselt):** `{user_profile['contact'][:10]}...`")

            st.markdown("### 📡 Deine Resonanzen")
            if st.button("Nach neuen Matches suchen"):
                with st.spinner("Analysiere das morphogenetische Feld..."):
                    best_match = None
                    max_sim = -1.0
                    
                    for entry in db:
                        # Sich selbst und nicht passende Geschlechter ausschließen
                        if entry['key_hash'] != v_hash and is_gender_match(
                            user_profile['gender'], user_profile['pref'], 
                            entry['gender'], entry['pref']
                        ):
                            sim = calculate_similarity(user_profile['vector'], entry['vector'])
                            if sim > max_sim:
                                max_sim = sim
                                best_match = entry
                    
                    if best_match:
                        st.balloons()
                        # Match-Anzeige im neuen Style-Box-Design
                        st.markdown(f"""
                        <div class="match-box">
                            <h3>🔥 Top Match Gefunden!</h3>
                            <p>Name: <strong>{best_match['name']}</strong></p>
                            <p>Resonanz: <span class="match-score">{int(max_sim*100)}%</span></p>
                            <p>Kontakt: <code>{decrypt_data(best_match['contact'])}</code></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Aktuell keine neuen Schwingungen, die deinem Filter entsprechen.")
                        
        else:
            # --- MODUS B: REGISTRIERUNG (Key unbekannt) ---
            st.info("Dieser Vibe Key ist neu. Erstelle jetzt dein Profil:")
            
            with st.form("registration_form"):
                col1, col2 = st.columns(2)
                with col1:
                    u_name = st.text_input("Dein Name / Alias")
                    u_gender = st.selectbox("Dein Geschlecht", ["m", "w", "d"])
                with col2:
                    u_contact = st.text_input("Kontakt (z.B. Signal/Telegram)")
                    u_pref = st.selectbox("Du suchst", ["m", "w", "d", "egal"])
                
                manifesto = st.text_area("Dein Manifesto (Wofür brennst du?)", height=200)
                
                submitted = st.form_submit_button("PROFIL SPEICHERN & VEKTOR ERZEUGEN")
                
                if submitted:
                    if not all([u_name, u_contact, manifesto]):
                        st.warning("Bitte fülle alle Felder aus!")
                    else:
                        with st.spinner("Verbinde mit dem OpenAI-Bewusstsein..."):
                            try:
                                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                                res = client.embeddings.create(input=manifesto, model="text-embedding-3-small")
                                user_vector = res.data[0].embedding
                                
                                new_entry = {
                                    "name": sanitize_input(u_name),
                                    "gender": u_gender,
                                    "pref": u_pref,
                                    "contact": encrypt_data(u_contact),
                                    "manifesto_hash": hash_key(manifesto),
                                    "vector": user_vector,
                                    "key_hash": v_hash
                                }
                                db.append(new_entry)
                                save_db(db)
                                
                                send_telegram_msg(f"✨ Neuer User im TST-System: {u_name} ({u_gender} sucht {u_pref})")
                                st.success("Profil erfolgreich erstellt! Du kannst jetzt den Vibe Key erneut eingeben, um dich einzuloggen.")
                                st.rerun() # Seite neu laden, damit der Login-Status aktualisiert wird

                            except Exception as e:
                                st.error(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()