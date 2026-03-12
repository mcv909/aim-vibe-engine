import streamlit as st

import streamlit as st

def apply_custom_style(): 
    """Erzwingt das helle Design und optimiert die Lesbarkeit massiv."""
    st.markdown(
        """
        <style>
        /* 1. GLOBALER LOOK */
        .stApp {
            background-color: #FFFFFF !important;
            color: #111111 !important;
        }

        /* 2. LABELS (Die Texte ÜBER den Eingabefeldern) */
        /* Wir zielen direkt auf die Streamlit-Markdown-Absätze in Labels ab */
        .stWidgetLabel p, label p {
            color: #000000 !important; /* Tiefschwarz */
            font-weight: 700 !important; /* Fett für bessere Sichtbarkeit */
            font-size: 1.05rem !important;
            opacity: 1 !important;
        }

        /* 3. PLACEHOLDER (Die Beispieltexte INNERHALB der Felder) */
        /* Diese müssen dunkler sein als der Standard, aber heller als die Labels */
        ::placeholder {
            color: #555555 !important; /* Deutliches Dunkelgrau */
            opacity: 1 !important;
        }
        input::placeholder, textarea::placeholder {
            color: #555555 !important;
            opacity: 1 !important;
        }

        /* 4. NAVIGATION BUTTONS OBEN (Grau & Lesbar) */
        div.stButton > button {
            background-color: #F0F2F6 !important; /* Helles Grau */
            color: #333333 !important; /* Dunkle Schrift */
            border: 1px solid #CCCCCC !important;
            font-weight: 500 !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            border-color: #FF00FF !important; /* AIM-Pink beim Hover */
            color: #FF00FF !important;
        }

        /* 5. INPUT FELDER (Inhalt schwarz auf weiß) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #BBBBBB !important;
        }
        
        /* Dropdown-Listen Fix (Inhalt schwarz) */
        div[data-baseweb="popover"], div[data-baseweb="menu"] {
            color: #000000 !important;
        }

        /* 6. ZENTRIERTE HEADER */
        .centered-header {
            text-align: center !important;
            display: block;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #000000;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
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

def render_nav():
    """Zentrales Navigations-Element für alle Seiten."""
    if 'menu' not in st.session_state:
        st.session_state.menu = "Manifesto erstellen"

    nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    if nav_cols[0].button("📝 Manifesto"): 
        st.session_state.menu = "Manifesto erstellen"
        st.switch_page("app.py")
    if nav_cols[1].button("🔑 Login"): 
        st.session_state.menu = "Login"
        st.switch_page("app.py")
    if nav_cols[2].button("🎯 Resonanz"): 
        st.switch_page("pages/qa.py")
    if nav_cols[3].button("ℹ️ Über AIM"): 
        st.switch_page("pages/about.py")
    if nav_cols[4].button("⚙️ Admin"): 
        st.session_state.menu = "Admin"
        st.switch_page("app.py")

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