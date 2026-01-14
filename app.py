import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from security import encrypt_data, sanitize_input, hash_key
from db_handler import load_db, save_db
from logic import get_coords
from style import set_page_style, render_header, render_visual_anchor

# --- INITIALISIERUNG ---
load_dotenv()
VERSION = "v0.7.5-RESILIENT-TST"

def check_key_strength(key):
    """Gibt Feedback zur Sicherheit des Keys."""
    if not key: return None
    if len(key) < 6: return "⚠️ Zu kurz", "#FF4B4B"
    if len(key) < 10: return "📡 Akzeptabel", "#1B263B"
    return "🔥 Sicher", "#1b5e20"

def main():
    st.set_page_config(page_title="I AM | AIM", layout="wide")
    set_page_style()
    
    # 1. Header & Build Info
    render_header()
    st.markdown(f'<div class="build-hint">SYSTEM_STATUS: {VERSION} // AIM_STABLE</div>', unsafe_allow_html=True)

    # 2. MODUS & KEY (Ganz oben)
    menu = st.radio("Modus wählen", ["Login", "Neues Profil erstellen"], horizontal=True)
    
    v_key_help = "Dein Passwort um Änderungen vorzunehmen, wenn du auf die Seite zurückkommst."
    
    if menu == "Login":
        v_key = st.text_input("Vibe Key", type="password", placeholder="Dein Key", help=v_key_help)
    else:
        v_key = st.text_input("Neuer Vibe Key", type="password", placeholder="Wähle einen Key", help=v_key_help)
        
        # Key-Validierung anzeigen
        strength = check_key_strength(v_key)
        if strength:
            st.markdown(f'<p style="color: {strength[1]}; font-size: 0.8rem; margin-top: -15px;">{strength[0]}</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. DAS BIN ICH (Das wichtigste Feld mit Tooltip)
    col_a, col_b = st.columns([1.2, 0.8])
    with col_a:
        st.subheader("Das bin ich")
        manifesto_help = (
            "Du arbeitest schon mit einer KI/AI? Lass dir ein Abstrakt von deiner Kommunikation ziehen! "
            "Weise sie Bspw. an: Bitte beschreib mich in 20 Sätzen. Nimm das und kopier es hier rein. "
            "Checke es gegen und verbessere es. Je mehr wir über dich wissen, desto besser/genauer wird "
            "dein Bild das wir von dir haben und damit auch die Vibe Berechnung."
        )
        manifesto = st.text_area(
            "Manifesto", 
            height=350, 
            placeholder="Schreib über alles was dich ausmacht...",
            label_visibility="collapsed",
            help=manifesto_help
        )
    with col_b:
        render_visual_anchor()

    st.divider()

    # 4. TECHNISCHE MERKMALE (Operative Daten)
    if menu == "Neues Profil erstellen":
        st.subheader("Technische Merkmale")
        c1, c2 = st.columns(2)
        with c1:
            u_name = st.text_input(
                "Identität / Name", 
                placeholder="Dein Nic oder Name",
                help="Dein Nic oder Name, wir brauchen keine Echtdaten. So sprechen wir dich bei Telegram an und das geben wir bei einem Match mit."
            )
            u_loc = st.text_input(
                "Präsenz / Ort", 
                placeholder="Stadtname",
                help="Stadtname wo du wohnst."
            )
            u_coords = get_coords(u_loc) if u_loc else None
            u_stature = st.selectbox("Deine Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"])
        
        with c2:
            u_contact = st.text_input(
                "Signal / Kontakt", 
                placeholder="@handle",
                help="Aktuell geht NUR Telegram, nimm hier einen Namen - es beginnt immer mit einem @."
            )
            u_radius = st.slider("Matching-Radius (km)", 5, 500, 50)
            u_target_stature = st.multiselect("Gesuchte Statur", ["zierlich", "sportlich", "durchschnittlich", "kräftig", "curvy"], default=["durchschnittlich"])
        
        # 5. DER ROTE BUTTON (Action!)
        if st.button("DNA SICHERN & RESONANZ STARTEN"):
            if all([u_name, u_contact, manifesto, v_key, u_coords]):
                st.success("DNA wird im Äther stabilisiert...")
                # ... Logik ...
            else:
                st.warning("Eingabe unvollständig. Check den Ort und das Manifesto.")

    elif menu == "Login":
        if st.button("RESONANZ PRÜFEN"):
            if v_key:
                st.info("Suche Resonanz-Muster...")
            else:
                st.warning("Bitte Vibe Key eingeben.")

if __name__ == "__main__":
    main()