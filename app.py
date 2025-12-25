import streamlit as st
import json
import pandas as pd
import plotly.express as px
import numpy as np  # <--- Das ist die neue Zeile 5

# --- MATHEMATISCHE KERNLOGIK ---
def calculate_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def run_vibe_check(user_a, user_b):
    results = []
    total_score = 0
    # ... Rest der Funktion wie oben ...
    return total_score, results

def main():

# --- LOGIK-TRANSPARENZ: KONFIGURATION ---
def load_master_profile():
    # Wir greifen auf dein in Lützow erstelltes Master-Profil zu [cite: 2025-12-25]
    with open('marc_master_profile.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Branding: Umstellung auf AIM VIBE
    st.set_page_config(page_title="AIM VIBE - Semantic Matching Engine", layout="wide")
    st.title("🎯 AIM VIBE")
    st.subheader("Finde deine Resonanz im 1.536-dimensionalen Raum")
    
    # Daten laden
    profile = load_master_profile()
    
    # Layout-Struktur
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write(f"### Profil: {profile['user']}")
        st.info(f"Standort: {profile.get('location', 'Lützow')}")
        
        # Darstellung der Säulen
        for pillar in profile['pillars']:
            with st.expander(f"Säule {pillar['id']}: {pillar['category']} (Gewichtung: {int(pillar['weight']*100)}%)"):
                st.write(f"*'{pillar['text']}'*")
                st.caption(f"Vektor-Dimensionen: {len(pillar['vector'])}")

    with col2:
        st.write("### Dein Vibe-Profil")
        df = pd.DataFrame(profile['pillars'])
        fig = px.pie(df, values='weight', names='category', 
                     title="Gewichtung der Core Values",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)

    # --- KI-ZWILLING & MATCHMAKING VORSCHAU ---
    st.divider()
    st.write("### 🧠 AIM VIBE Status: Bereit für den Match")
    st.progress(0.4) 
    
    if st.button("Starte Vibe-Check Simulation"):
        st.success("Logik-Schnittstelle aktiv: Suche nach semantischer Nähe...")
        st.write("Warte auf den Ivee-Vektor für den ersten Real-Life-Vergleich.")

    # --- SIDEBAR: EXPORT & BRANDING ---
    st.sidebar.title("AIM VIBE Control")
    st.sidebar.write("### 📄 Portfolio-Export")
    
    export_data = {
        "Brand": "AIM VIBE",
        "User": profile['user'],
        "Säulen": [{p['category']: p['text']} for p in profile['pillars']],
        "Vektor-Modell": "text-embedding-3-small"
    }
    
    json_string = json.dumps(export_data, indent=4, ensure_ascii=False)
    st.sidebar.download_button(
        label="Download Profile (JSON)",
        file_name=f"AIM_VIBE_Profile_{profile['user'].replace(' ', '_')}.json",
        mime="application/json",
        data=json_string
    )
    
    if st.sidebar.button("Show Pitch-Deck Tip"):
        st.sidebar.info("💡 **Startup-Tipp:** Nutze das Tortendiagramm als 'Core Value Matrix' in deinem Pitch-Deck, um Investoren die Tiefe deines Matchings zu demonstrieren.")

if __name__ == "__main__":
    main()