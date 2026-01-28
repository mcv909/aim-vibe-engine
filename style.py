import streamlit as st

def apply_custom_style(): # Name angepasst an deinen app.py Call!
    """Wiederherstellung des hellen Produktions-Looks (v0.4.2 Style)."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #262730;
        }
        h1, h2, h3 {
            color: #000000 !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 200;
            text-align: center;
        }
        /* Card-Optik für Formulare */
        div[data-testid="stForm"] {
            background-color: #F0F2F6;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #E6E9EF;
        }
        /* Input Felder weiß */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {
            background-color: white !important;
        }
        /* Spezieller Beta-Footer Style */
        .beta-container {
            background-color: #F0F2F6;
            padding: 25px;
            border-radius: 5px;
            margin-top: 50px;
            color: #555;
            font-size: 0.85rem;
            line-height: 1.6;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_header():
    """Minimalistischer Header (Prod-Style)."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px; margin-bottom: 20px;">
            <h1 style="letter-spacing: 5px;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6;">AI-Matching basierend auf Resonanz, nicht auf Checklisten.</p>
        </div>
        """, unsafe_allow_html=True
    )

def render_beta_footer():
    """Der Transparenz-Block aus der Produktion."""
    st.markdown(
        """
        <div class="beta-container">
            <h3 style="text-align: left; font-size: 1.2rem; font-weight: 400;">Beta-Status & Transparenz</h3>
            <p>Wir befinden uns aktuell im <b>Beta-Stadium</b>. Bitte seht es uns nach, falls noch nicht alles 100% rund läuft.<br>
            <b>Wichtig:</b> Notiert euch euren persönlichen Code, um euren Eintrag später anzupassen.</p>
            <p><b>Datenschutz:</b> Anonymität ist Key. Selbst als Admins können wir keine direkten Bezüge von Einträgen zu realen Personen herstellen.</p>
            <p>Anregungen an: <a href="mailto:marc.c.vietor@gmail.com">marc.c.vietor@gmail.com</a></p>
        </div>
        """, unsafe_allow_html=True
    )