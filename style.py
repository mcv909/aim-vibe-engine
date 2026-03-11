import streamlit as st

def apply_custom_style(): 
    """Erzwingt das helle Design, macht Buttons lesbar und fixiert die Nav."""
    st.markdown(
        """
        <style>
        /* FARB-DEFINITIONEN (Hier kannst du einfach ändern) */
        :root {
            --aim-bg: #FFFFFF;
            --aim-text: #111111;
            --aim-gray-light: #F0F2F6;
            --aim-gray-medium: #DDDDDD;
            --aim-accent: #FF00FF;
        }

        .stApp {
            background-color: var(--aim-bg) !important;
            color: var(--aim-text) !important;
        }

        /* 1. NAVIGATION BUTTONS (Grau, klar entzifferbar) */
        div.stButton > button {
            background-color: #EEEEEE !important;
            color: #333333 !important;
            border: 1px solid var(--aim-gray-medium) !important;
            font-weight: 500 !important;
            width: 100%;
        }
        div.stButton > button:hover {
            border-color: var(--aim-accent) !important;
            color: var(--aim-accent) !important;
        }

        /* 2. INPUT FELDER (Weißer Hintergrund, schwarze Schrift) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #DDDDDD; !important;
            border: 1px solid var(--aim-gray-medium) !important;
        }
        
        /* Fix für die Lesbarkeit im Dropdown-Menü */
        div[data-baseweb="popover"] {
            color: #000000 !important;
        }

        /* 3. ZENTRIERTE ELEMENTE */
        .centered-header {
            text-align: center !important;
            display: block;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            color: #000000;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* 4. TOP-NAV FIXIERUNG */
        [data-testid="stHeader"] {
            position: fixed;
            top: 0;
            z-index: 1000;
            width: 100%;
            background-color: #FFFFFF !important;
            border-bottom: 1px solid var(--aim-gray-medium);
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