import streamlit as st

def apply_custom_style(): 
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF !important; color: #111111 !important; }
        
        /* 1. SLIDER-FIX: Aktive Leiste & Werte in Dunkelgrün, Hintergrund hell */
        /* Die Schiene hinter dem Regler */
        .stSlider > div [data-baseweb="slider"] > div:first-child {
            background-color: #F0F2F6 !important;
        }
        /* Die aktive Strecke (der Bereich zwischen/bis zu den Thumbs) */
        .stSlider > div [data-baseweb="slider"] > div:first-child > div:nth-child(2) {
            background-color: #1E5631 !important;
        }
        /* Die Zahlen-Labels über den Reglern */
        .stSlider [data-testid="stThumbValue"] {
            color: #1E5631 !important;
            font-weight: bold;
        }

        /* 2. NAVIGATION: Aktiv-State (Schwarz mit negativer Typo) */
        .active-nav-btn button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #000000 !important;
            font-weight: 700 !important;
        }

        /* 3. INPUTS: Grau wie gewünscht */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #F0F2F6 !important;
            border: 1px solid #CCCCCC !important;
        }

        .stWidgetLabel p { color: #000000 !important; font-weight: 700 !important; }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    # Erkennung der aktiven Seite/Menü [cite: 2026-03-12]
    current_menu = st.session_state.get('menu', "Manifesto erstellen")
    current_page = st.source_code_path.split("/")[-1] if hasattr(st, "source_code_path") else ""

    nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    
    # Helfer für das Highlighting
    def nav_class(target_menu, target_page=None):
        if target_page and current_page == target_page: return "active-nav-btn"
        if current_menu == target_menu and current_page not in ["qa.py", "about.py"]: return "active-nav-btn"
        return ""

    with nav_cols[0]:
        st.markdown(f'<div class="{nav_class("Manifesto erstellen")}">', unsafe_allow_html=True)
        if st.button("✎ Manifesto"): 
            st.session_state.menu = "Manifesto erstellen"
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[1]:
        st.markdown(f'<div class="{nav_class("Login")}">', unsafe_allow_html=True)
        if st.button("⚿ Login"): 
            st.session_state.menu = "Login"
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[2]:
        st.markdown(f'<div class="{nav_class(None, "qa.py")}">', unsafe_allow_html=True)
        if st.button("◬ Resonanz"): st.switch_page("pages/qa.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[3]:
        st.markdown(f'<div class="{nav_class(None, "about.py")}">', unsafe_allow_html=True)
        if st.button("ⓘ Über AIM"): st.switch_page("pages/about.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[4]:
        st.markdown(f'<div class="{nav_class("Admin")}">', unsafe_allow_html=True)
        if st.button("⚙ Admin"): 
            st.session_state.menu = "Admin"
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

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
    if 'menu' not in st.session_state:
        st.session_state.menu = "Manifesto erstellen"

    # Wir nutzen dezentere, technische Symbole
    nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    
    if nav_cols[0].button("✎ Manifesto"): 
        st.session_state.menu = "Manifesto erstellen"
        st.switch_page("app.py")
    if nav_cols[1].button("⚿ Login"): 
        st.session_state.menu = "Login"
        st.switch_page("app.py")
    if nav_cols[2].button("◬ Resonanz"): # Das Delta-Symbol für Veränderung/Vibe
        st.switch_page("pages/qa.py")
    if nav_cols[3].button("ⓘ Über AIM"): 
        st.switch_page("pages/about.py")
    if nav_cols[4].button("⚙ Admin"): 
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