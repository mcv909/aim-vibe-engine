import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# UNSERE MODULE
from security import encrypt_data, decrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import calculate_similarity, is_gender_match, send_telegram_msg
from style import set_page_style, render_header

load_dotenv()
VERSION = "v0.7.0-FULL-TST"

def main():
    st.set_page_config(page_title="I AM | AIM (Test)", layout="wide", initial_sidebar_state="collapsed")
    set_page_style()
    
    st.title(f"🧬 [i am] | {VERSION}")
    render_header()

    # DIE NEUE LOGIK-WEICHE
    menu = st.radio("Was hast du vor?", ["Einloggen", "Neues Profil erstellen"], horizontal=True)
    st.markdown("---")

    if menu == "Einloggen":
        st.markdown("### 🔑 Zugang zum morphogenetischen Feld")
        vibe_key = st.text_input("Gib deinen Vibe Key ein", type="password")
        
        if st.button("RESONANZ PRÜFEN"):
            if not vibe_key:
                st.warning("Bitte gib deinen Key ein.")
                return
            
            db = load_db()
            v_hash = hash_key(vibe_key)
            user = next((i for i in db if i.get("key_hash") == v_hash), None)
            
            if user:
                st.success(f"Willkommen zurück, {user['name']}!")
                # Hier folgt die Match-Logik (siehe vorherige Versionen)
                st.info("Suche nach Resonanzen läuft...")
            else:
                st.error("Key unbekannt. Bist du neu hier?")

    else:
        st.markdown("### 🧬 Deine DNA hinterlegen")
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            with col1:
                u_name = st.text_input("Identität (Name / Alias)")
                u_age = st.number_input("Dein Alter", 18, 99, 30)
                u_location = st.text_input("Dein Ort")
                u_height = st.slider("Körpergröße (cm)", 140, 220, 175)
                u_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "athletisch", "durchschnittlich", "kräftig", "curvy"])
            with col2:
                u_contact = st.text_input("Signal / Telegram Kontakt")
                u_radius = st.slider("Such-Umkreis (km)", 5, 500, 50)
                u_age_range = st.slider("Alters-Spektrum", 18, 99, (25, 45))
                u_smoker = st.selectbox("Raucher?", ["Nein", "Gelegentlich", "Ja"])
                u_target_stature = st.multiselect("Gesuchte Statur(en)", ["zierlich", "sportlich", "athletisch", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])

            manifesto = st.text_area("Dein Manifesto (Drogen, Techno, Werte - schreib frei!)", height=200)
            v_key_new = st.text_input("Wähle deinen Vibe Key (Sicher aufbewahren!)", type="password")
            
            if st.form_submit_button("DNA SICHERN & RESONANZ STARTEN"):
                if not all([u_name, u_contact, manifesto, v_key_new]):
                    st.warning("Bitte alle Pflichtfelder ausfüllen!")
                    return

                with st.spinner("Vektorisierung läuft..."):
                    try:
                        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                        res = client.embeddings.create(input=manifesto, model="text-embedding-3-small")
                        
                        new_entry = {
                            "key_hash": hash_key(v_key_new),
                            "name": sanitize_input(u_name),
                            "age": u_age,
                            "location": u_location,
                            "radius": u_radius,
                            "age_range": u_age_range,
                            "height": u_height,
                            "smoker": u_smoker,
                            "contact": encrypt_data(u_contact),
                            "manifesto_enc": encrypt_data(manifesto), # Für Modell-Wechsel gesichert
                            "vector": res.data[0].embedding,
                            "meta": {"model": "text-embedding-3-small", "ver": VERSION},
                            "stature": u_stature,
                            "target_stature": u_target_stature,
                            "coords": coords, # Speichern für schnellen Distanzcheck
                        }
                        
                        db = load_db()
                        db.append(new_entry)
                        save_db(db)
                        
                        # DER GENIALE TEIL: Key per Telegram senden
                        msg = f"✨ *Willkommen bei I AM!*\n\nDein Profil wurde erstellt.\n🔑 Dein Vibe Key: `{v_key_new}`\n\nBewahre diese Nachricht gut auf!"
                        send_telegram_msg(msg)
                        
                        st.success("Profil gesichert! Dein Vibe Key wurde dir per Telegram zugestellt.")
                    except Exception as e:
                        st.error(f"Fehler: {e}")

if __name__ == "__main__":
    main()