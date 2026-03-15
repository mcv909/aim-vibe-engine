import streamlit as st

def apply_custom_style(): 
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF !important; color: #111111 !important; }
        
        /* 1. SLIDER: Rot durch GRÜN ersetzen */
        /* Die aktive Leiste zwischen den Reglern */
        div[data-baseweb="slider"] > div > div {
            background-image: linear-gradient(to right, #1E5631 0%, #1E5631 100%) !important;
            background-color: #1E5631 !important;
        }
        /* Die Regler-Knöpfe selbst */
        div[role="slider"] {
            background-color: #1E5631 !important;
            border: 2px solid #1E5631 !important;
        }
        /* Die Zahlenwerte über dem Slider */
        div[data-testid="stThumbValue"] {
            color: #1E5631 !important;
            font-weight: bold !important;
        }

        /* 2. NAVIGATION: Standard hell, Aktiv Schwarz */
        div.stButton > button {
            background-color: #F0F2F6 !important; /* Hellgrau als Standard */
            color: #333333 !important;
            border: 1px solid #CCCCCC !important;
        }
        
        .active-nav-btn button {
            background-color: #000000 !important; /* Schwarz nur für Aktiv */
            color: #FFFFFF !important;
            border: 1px solid #000000 !important;
            font-weight: 700 !important;
        }

        /* 3. INPUTS & TEXTAREA */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    """Zentrale Navigation mit aktivem Status-Highlighting."""
    current_menu = st.session_state.get('menu', "Manifesto erstellen")
    # Erkennung der Seite für das Highlighting [cite: 2026-03-12]
    current_page = st.source_code_path.split("/")[-1] if hasattr(st, "source_code_path") else "app.py"

    nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    
    def nav_class(target_menu, target_page=None):
        if target_page and current_page == target_page: return "active-nav-btn"
        if current_menu == target_menu and current_page == "app.py": return "active-nav-btn"
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
    st.markdown('<div style="text-align: center; margin-top: 20px;"><h1 style="letter-spacing: 5px; font-size: 3rem; margin-bottom: 0;">[ I  A  M ]  |  A I M</h1><p style="opacity: 0.6; font-size: 1.1rem;">Authentic Intelligence Mate</p></div>', unsafe_allow_html=True)

def render_beta_footer():
    st.markdown('<div style="background-color: #F0F2F6; padding: 25px; border-radius: 5px; margin-top: 50px;"><h3 style="text-align: left; font-size: 1.2rem;">Beta-Status & Transparenz</h3><p>AIM ist ein Experiment in Resonanz. Dein Vibe Key ist dein einziger Zugang.</p></div>', unsafe_allow_html=True)

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