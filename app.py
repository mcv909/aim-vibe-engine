import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from security import encrypt_data, decrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import calculate_similarity, get_coords
from style import set_page_style, render_header, render_visual_anchor

# --- INITIALISIERUNG ---
load_dotenv()
VERSION = "v0.7.5-RESILIENT-TST"

def main():
    st.set_page_config(page_title="I AM | AIM", layout="wide")
    set_page_style()
    
    # 1. Header & Build Info
    render_header()
    st.markdown(f'<div class="build-hint">SYSTEM_STATUS: {VERSION} // AIM_STABLE</div>', unsafe_allow_html=True)

    # 2. MODUS & KEY (Nach oben verschoben)
    menu = st.radio("Modus wählen", ["Login", "Neues Profil erstellen"], horizontal=True)
    
    # Der Key kommt jetzt direkt unter die Modus-Wahl
    v_key = ""
    if menu == "Login":
        v_key = st.text_input("Vibe Key", type="password", placeholder="Dein Key für den Login")
    else:
        v_key = st.text_input("Neuer Vibe Key", type="password", placeholder="Wähle einen Key für deine DNA")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. DAS BIN ICH (Manifesto & Mona Lisa)
    col_a, col_b = st.columns([1.2, 0.8])
    with col_a:
        st.subheader("Das bin ich")
        manifesto = st.text_area(
            "Schreib über alles was dich ausmacht...", 
            height=350, 
            placeholder="Die Vorlage. Dein qualitativer Anker. Je mehr du hier mitgibst, desto schärfer wird dein Matching-Bild...",
            label_visibility="collapsed"
        )
    with col_b:
        render_visual_anchor()

    st.divider()

    # 4. OPERATIVE DATEN (Technische Merkmale unter dem Manifesto)
    if menu == "Neues Profil erstellen":
        st.subheader("Technische Merkmale")
        c1, c2 = st.columns(2)
        with c1:
            u_name = st.text_input("Identität / Name")
            u_loc = st.text_input("Präsenz / Ort")
            u_coords = get_coords(u_loc) if u_loc else None
            u_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
        with c2:
            u_contact = st.text_input("Signal / Kontakt")
            u_radius = st.slider("Matching-Radius (km)", 5, 500, 50)
            u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])
        
        # 5. DER ROTE BUTTON (Einziges rotes Element)
        if st.button("DNA SICHERN & RESONANZ STARTEN"):
            if all([u_name, u_contact, manifesto, v_key, u_coords]):
                # Logik-Aufruf
                st.success("DNA gesichert. Suche nach Resonanz...")
            else:
                st.warning("Matrix lückenhaft. Bitte alle Felder (inkl. Ort) prüfen.")

    elif menu == "Login":
        if st.button("RESONANZ PRÜFEN"):
            if v_key:
                st.info("Prüfe Resonanz-Frequenzen...")
            else:
                st.warning("Bitte Vibe Key eingeben.")

if __name__ == "__main__":
    main()