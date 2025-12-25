import streamlit as st
import json
import pandas as pd
import plotly.express as px

# --- LOGIK-TRANSPARENZ: KONFIGURATION ---
# Wir laden das Master-Profil, das wir in Lützow erstellt haben [cite: 2025-12-25]
def load_master_profile():
    with open('marc_master_profile.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Branding & Vision (Portfolio-Aspekt)
    st.set_page_config(page_title="AIM - Semantic Matching Engine", layout="wide")
    st.title("🎯 AIM: AI Matchmaker")
    st.subheader("Die Vektorisierung der menschlichen Essenz")
    
    # Daten laden
    profile = load_master_profile()
    
    # Layout-Struktur: Links Profil-Details, Rechts Visualisierung
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write(f"### Profil: {profile['user']}")
        st.info(f"Standort: {profile.get('location', 'Lützow')}")
        
        # Darstellung der Säulen (Transparenz für den User)
        for pillar in profile['pillars']:
            with st.expander(f"Säule {pillar['id']}: {pillar['category']} (Gewichtung: {int(pillar['weight']*100)}%)"):
                st.write(f"*'{pillar['text']}'*")
                st.caption(f"Vektor-Dimensionen: {len(pillar['vector'])}")

    with col2:
        st.write("### Der Vietor-Vektor im Raum")
        # Visualisierung der Gewichtung (Wirkursache)
        df = pd.DataFrame(profile['pillars'])
        fig = px.pie(df, values='weight', names='category', 
                     title="Gewichtung der Core Values",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)

    # --- BIG PICTURE: KI-ZWILLING VORSCHAU ---
    st.divider()
    st.write("### 🧠 KI-Zwilling Status: Bereit für Interaktion")
    st.progress(0.4) # Simulierter Fortschritt der Zwilling-Integration
    
    if st.button("Starte Vibe-Check Simulation"):
        st.success("Logik-Schnittstelle aktiv: Vergleiche 1.536 Dimensionen...")
        st.write("Nächster Schritt: Integration des Gegenprofils.")

if __name__ == "__main__":
    main()