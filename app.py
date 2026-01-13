import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from security import encrypt_data, decrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import calculate_similarity, is_gender_match, is_stature_match, send_telegram_msg, get_coords, calculate_distance
from style import set_page_style, render_header

load_dotenv()
VERSION = "v0.7.5-RESILIENT-TST"

def main():
    st.set_page_config(page_title="I AM | AIM (Test)", layout="wide")
    set_page_style()
    st.title(f"🧬 [i am] | {VERSION}")
    render_header()

    # Session State Airbag
    if 'manifesto_buffer' not in st.session_state: st.session_state.manifesto_buffer = ""

    menu = st.radio("Modus wählen", ["Login", "Neues Profil erstellen"], horizontal=True)

    if menu == "Login":
        v_key = st.text_input("Vibe Key", type="password")
        if st.button("RESONANZ PRÜFEN"):
            db = load_db()
            user = next((i for i in db if i.get("key_hash") == hash_key(v_key)), None)
            if user:
                st.success(f"Willkommen, {user['name']}!")
                # Hier Matching-Logik einbauen (Haversine & Vector)
            else: st.error("Key unbekannt.")

    else:
        col1, col2 = st.columns(2)
        with col1:
            u_name = st.text_input("Name / Alias")
            u_loc = st.text_input("Ort")
            u_coords = get_coords(u_loc) if u_loc else None
            if u_coords: st.success(f"📍 Lokalisiert: {u_coords[0]:.2f}, {u_coords[1]:.2f}")
            u_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
        with col2:
            u_contact = st.text_input("Signal / Kontakt")
            u_radius = st.slider("Radius (km)", 5, 500, 50)
            u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])
        
        manifesto = st.text_area("Dein Manifesto", value=st.session_state.manifesto_buffer, height=200)
        st.session_state.manifesto_buffer = manifesto
        v_key_new = st.text_input("Neuer Vibe Key", type="password")

        if st.button("DNA SICHERN"):
            if all([u_name, u_contact, manifesto, v_key_new, u_coords]):
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                res = client.embeddings.create(input=manifesto, model="text-embedding-3-small")
                
                new_entry = {
                    "key_hash": hash_key(v_key_new), "name": sanitize_input(u_name),
                    "coords": u_coords, "stature": u_stature, "target_stature": u_target_stature,
                    "contact": encrypt_data(u_contact), "manifesto_enc": encrypt_data(manifesto),
                    "vector": res.data[0].embedding, "meta": {"ver": VERSION}
                }
                save_db(load_db() + [new_entry])
                send_telegram_msg(f"✨ Neuer User: {u_name}\n🔑 Key: `{v_key_new}`")
                st.session_state.manifesto_buffer = ""
                st.success("Profil gesichert! Key ist per Telegram raus.")
            else: st.warning("Daten unvollständig oder Ort nicht gefunden!")

if __name__ == "__main__": main()