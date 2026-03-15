import streamlit as st

def apply_custom_style(): 
    """Erzwingt das helle Design, graue Inputs und dunkelgrüne Slider."""
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF !important; color: #111111 !important; }
        
        /* 1. LABELS & PLACEHOLDER */
        .stWidgetLabel p, label p { color: #000000 !important; font-weight: 700 !important; }
        ::placeholder { color: #555555 !important; }

        /* 2. INPUTS (Grauer Hintergrund) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
            border: 1px solid #CCCCCC !important;
        }

        /* 3. SLIDER (Dunkelgrün) */
        .stSlider [data-baseweb="slider"] { background-color: #1E5631 !important; }

        /* 4. NAVIGATION & ACTIVE STATE */
        div.stButton > button {
            background-color: #F0F2F6 !important;
            color: #333333 !important;
            border: 1px solid #CCCCCC !important;
        }
        /* Highlight für die aktive Seite */
        .active-nav-btn button {
            border-bottom: 3px solid #FF00FF !important;
            background-color: #E6E9EF !important;
            font-weight: bold !important;
        }

        .centered-header {
            text-align: center !important;
            display: block;
            margin-top: 2rem;
            color: #000000;
            font-weight: 800;
            text-transform: uppercase;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    # Wir bestimmen die aktuelle Seite anhand des Dateinamens
    current_page = st.source_code_path.split("/")[-1] if hasattr(st, "source_code_path") else ""
    
    nav_cols = st.columns([1.5, 0.8, 1.2, 1, 0.8])
    
    # Helfer für das Highlighting
    def get_nav_class(page_name):
        return "active-nav-btn" if current_page == page_name else ""

    with nav_cols[0]:
        st.markdown(f'<div class="{get_nav_class("app.py")}">', unsafe_allow_html=True)
        if st.button("✎ Manifesto"): 
            st.session_state.menu = "Manifesto erstellen"
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[1]:
        # Login ist Teil der app.py, daher Check auf Menu-State
        is_login = get_nav_class("app.py") if st.session_state.get('menu') == "Login" else ""
        st.markdown(f'<div class="{is_login}">', unsafe_allow_html=True)
        if st.button("⚿ Login"): 
            st.session_state.menu = "Login"
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[2]:
        st.markdown(f'<div class="{get_nav_class("qa.py")}">', unsafe_allow_html=True)
        if st.button("◬ Resonanz"): st.switch_page("pages/qa.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[3]:
        st.markdown(f'<div class="{get_nav_class("about.py")}">', unsafe_allow_html=True)
        if st.button("ⓘ Über AIM"): st.switch_page("pages/about.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with nav_cols[4]:
        is_admin = get_nav_class("app.py") if st.session_state.get('menu') == "Admin" else ""
        st.markdown(f'<div class="{is_admin}">', unsafe_allow_html=True)
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