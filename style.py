import streamlit as st

def apply_custom_style(): 
    """Erzwingt das helle Design und fixiert die Navigation."""
    st.markdown(
        """
        <style>
        /* 1. GLOBALER LIGHT-MODE FIX */
        .stApp {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }

        /* 2. TOP-NAV FIXIERUNG & FARBE */
        [data-testid="stHeader"] {
            position: fixed;
            top: 0;
            z-index: 1000;
            width: 100%;
            background-color: #FFFFFF !important;
            border-bottom: 1px solid #DDDDDD;
        }

        /* 3. ZENTRIERTE ELEMENTE */
        .centered-header {
            text-align: center !important;
            display: block;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            color: #111111;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 1.4rem;
        }

        h1, h2, h3 {
            color: #000000 !important;
            text-align: center !important;
        }

        /* 4. FORMULAR OPTIK (Hell & Klar) */
        div[data-testid="stForm"] {
            background-color: #F8F9FB;
            border: 1px solid #E6E9EF;
            border-radius: 12px;
        }
        
        /* Input Felder */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {
            background-color: white !important;
            color: #111111 !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_header():
    """Minimalistischer Header mit Logo-Vibe."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 10px;">
            <h1 style="letter-spacing: 5px; font-size: 3rem; margin-bottom: 0;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6; font-size: 1.1rem;">Authentic Intelligence Mate</p>
        </div>
        """, unsafe_allow_html=True
    )

def render_beta_footer():
    """Der Transparenz-Block für den finalen Vibe."""
    st.markdown(
        """
        <div class="beta-container">
            <h3 style="text-align: left !important; font-size: 1.2rem; font-weight: 400;">Beta-Status & Transparenz</h3>
            <p>Wir befinden uns aktuell im <b>Beta-Stadium</b>. AIM ist ein Experiment in Resonanz.<br>
            <b>Wichtig:</b> Dein Vibe Key ist dein einziger Zugang. Verliere ihn nicht.</p>
            <p><b>Datenschutz:</b> Verschlüsselung ist bei uns kein Feature, sondern das Fundament. Selbst wir können dein Manifesto nicht lesen.</p>
            <p>Anregungen: <a href="mailto:feedback@iam-aim.com">feedback@iam-aim.com</a></p>
        </div>
        """, unsafe_allow_html=True
    )

CSS_STÖRER = """
<style>
.aim-ribbon {
    position: fixed;
    top: 20px;
    right: -35px;
    background-color: #ff4b4b;
    color: white;
    padding: 5px 40px;
    transform: rotate(45deg);
    z-index: 2000;
    font-weight: bold;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    pointer-events: none;
}
</style>
"""