import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from security import encrypt_data, decrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import calculate_similarity, is_gender_match, is_stature_match, send_telegram_msg, get_coords, calculate_distance
from style import set_page_style, render_header, render_visual_anchor

# --- INITIALISIERUNG ---
load_dotenv()
VERSION = "v0.7.5-RESILIENT-TST"

def main():
    # 1. Page Config & Globaler Style
    st.set_page_config(page_title="I AM | AIM (Test)", layout="wide")
    set_page_style()
    
    # 2. Header & Technischer Status (Dunkelgrün, Console-Look)
    render_header()
    st.markdown(f'<div class="build-hint">SYSTEM_STATUS: {VERSION} // STABLE_BUILD // AIM_READY</div>', unsafe_allow_html=True)

    # 3. Session State Airbag
    if 'manifesto_buffer' not in st.session_state: 
        st.session_state.manifesto_buffer = ""

    # 4. DAS BIN ICH - Der qualitative Anker (Manifesto & Mona Lisa)
    # Hier ziehen wir das Layout bündig: Links der Text, rechts die Visualisierung
    col_a, col_b = st.columns([1.2, 0.8])
    
    with col_a:
        st.subheader("Das bin ich")
        manifesto = st.text_area(
            "Schreib über alles was dich ausmacht...", 
            value=st.session_state.manifesto_buffer,
            height=350, 
            placeholder="Die Vorlage. Dein qualitativer Anker. Je mehr du hier mitgibst, desto schärfer wird dein Matching-Bild. Schreib über alles was dich ausmacht - das kann und sollte auch jenseits von harten Fakten sein ;).",
            label_visibility="collapsed"
        )
        st.session_state.manifesto_buffer = manifesto

    with col_b:
        # Die Mona-Lisa-Boxen zur intuitiven Erklärung des Inputs
        render_visual_anchor()

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # 5. Operative Sektion (Modus-Wahl & Datenfelder)
    menu = st.radio("Modus wählen", ["Login", "Neues Profil erstellen"], horizontal=True)

    if menu == "Login":
        v_key = st.text_input("Vibe Key", type="password", help="Dein privater Schlüssel zur Resonanz.")
        if st.button("RESONANZ PRÜFEN"):
            db = load_db()
            user = next((i for i in db if i.get("key_hash") == hash_key(v_key)), None)
            if user:
                st.success(f"Willkommen zurück, {user['name']}!")
                # Matching-Berechnung folgt hier
            else: 
                st.error("Key unbekannt. Vielleicht ein Tippfehler in der Matrix?")

    else:
        # "Neues Profil erstellen" Bereich
        c1, c2 = st.columns(2)
        
        with c1:
            u_name = st.text_input("Identität / Name / Alias", placeholder="Wie sollen wir dich nennen?")
            u_loc = st.text_input("Präsenz / Ort", placeholder="Obertshausen, Lützow...")
            u_coords = get_coords(u_loc) if u_loc else None
            
            if u_coords: 
                st.success(f"📍 Lokalisiert: {u_coords[0]:.2f}, {u_coords[1]:.2f}")
            
            u_stature = st.selectbox(
                "Deine Statur", 
                ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"]
            )
            
        with c2:
            u_contact = st.text_input("Signal / Kontakt", placeholder="@handle oder E-Mail")
            u_radius = st.slider("Matching-Radius (km)", 5, 500, 50)
            u_target_stature = st.multiselect(
                "Gesuchte Statur", 
                ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], 
                default=["durchschnittlich"]
            )
        
        v_key_new = st.text_input("Neuer Vibe Key", type="password", help="Wähle einen sicheren Schlüssel für deine DNA.")

        # 6. Button: DNA Sichern & Telegram Signal
        if st.button("DNA SICHERN & RESONANZ STARTEN"):
            if all([u_name, u_contact, manifesto, v_key_new, u_coords]):
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Embedding erzeugen
                res = client.embeddings.create(input=manifesto, model="text-embedding-3-small")
                
                new_entry = {
                    "key_hash": hash_key(v_key_new), 
                    "name": sanitize_input(u_name),
                    "coords": u_coords, 
                    "stature": u_stature, 
                    "target_stature": u_target_stature,
                    "contact": encrypt_data(u_contact), 
                    "manifesto_enc": encrypt_data(manifesto),
                    "vector": res.data[0].embedding, 
                    "meta": {"ver": VERSION}
                }
                
                # Speichern & Benachrichtigen
                save_db(load_db() + [new_entry])
                send_telegram_msg(f"✨ Neue DNA im System: {u_name}\n📍 Ort: {u_loc}")
                
                st.session_state.manifesto_buffer = ""
                st.success("DNA erfolgreich gesichert. Dein Signal wurde im Äther platziert.")
            else: 
                st.warning("Die Matrix ist lückenhaft. Bitte Name, Kontakt, Manifesto, Key und Ort (lokalisiert) prüfen.")

# --- START ---
if __name__ == "__main__":
    main()