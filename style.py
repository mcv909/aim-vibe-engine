import streamlit as st

# Zentrales CD (Corporate Design) [cite: 2026-01-17]
CD_WEISS = "#FFFFFF"
CD_SCHWARZ = "#111111"
CD_GRAU_HELL = "#F8F9FB"
CD_NEON_GRUEN = "#39FF14"

CSS_STÖRER = """
<style>
.aim-ribbon {
    position: fixed;
    top: 40px;
    right: -45px;
    background-color: #ff4b4b;
    color: white;
    padding: 8px 50px;
    transform: rotate(45deg);
    z-index: 99999;
    font-weight: bold;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
</style>
"""

def init_global_state():
    if 'menu' not in st.session_state: 
        st.session_state.menu = "Manifesto erstellen"
    if 'manifesto_buffer' not in st.session_state: 
        st.session_state.manifesto_buffer = ""
    if 'logged_in' not in st.session_state: 
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state: 
        st.session_state.user_data = {}

def apply_custom_style(): 
    st.markdown(
        f"""
        <style>
        header {{ visibility: hidden !important; height: 0px !important; }}
        .stAppHeader {{ display: none !important; }}
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        .stApp {{ background-color: {CD_WEISS} !important; color: {CD_SCHWARZ} !important; }}
        .stMarkdown p, label, .stWidgetLabel p {{ color: {CD_SCHWARZ} !important; font-weight: 700 !important; }}
        .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div {{
            background-color: {CD_WEISS} !important; color: {CD_SCHWARZ} !important; border: 1px solid #CCCCCC !important;
        }}
        div.stButton > button {{
            width: 100% !important; background-color: {CD_GRAU_HELL} !important; color: {CD_SCHWARZ} !important;
            border: 1px solid #DDDDDD !important; padding: 12px !important; font-weight: 600 !important;
        }}
        button[kind="primary"], button[kind="primaryFormSubmit"] {{
            background-color: {CD_SCHWARZ} !important; color: {CD_WEISS} !important; border: 1px solid {CD_SCHWARZ} !important;
        }}
        .active-nav-btn button {{ background-color: {CD_SCHWARZ} !important; color: {CD_WEISS} !important; }}
        div[data-baseweb="slider"] > div {{ background-color: {CD_WEISS} !important; }}
        div[data-baseweb="slider"] > div > div:first-child {{ background-color: {CD_SCHWARZ} !important; }}
        div[data-baseweb="slider"] > div > div > div {{ background-color: {CD_NEON_GRUEN} !important; background-image: none !important; }}
        div[role="slider"] {{ background-color: {CD_SCHWARZ} !important; border: 2px solid {CD_NEON_GRUEN} !important; }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    init_global_state()
    cols = st.columns(4)
    # Mapping von Label zu (Menü-Status, Dateiname)
    menus = [
        ("✎ Manifesto", "Manifesto erstellen", "app.py"),
        ("⚿ Login", "Login", "app.py"),
        ("◬ Resonanz", "Resonanz", "qa.py"),
        ("ⓘ Über AIM", "Über AIM", "about.py"),
    ]
    
    for i, (label, menu_val, target_file) in enumerate(menus):
        with cols[i]:
            # Aktiven Status nur über den Menü-Wert prüfen, das ist am stabilsten
            is_active = (st.session_state.menu == menu_val)
            st.markdown(f'<div class="{"active-nav-btn" if is_active else ""}">', unsafe_allow_html=True)
            
            # UNIQUE KEY FIX: Wir nutzen den Menü-Wert im Key [cite: 2026-03-12]
            if st.button(label, key=f"btn_nav_{menu_val.replace(' ', '_')}"):
                st.session_state.menu = menu_val 
                if target_file == "app.py":
                    st.switch_page("app.py")
                else:
                    st.switch_page(f"pages/{target_file}")
            st.markdown('</div>', unsafe_allow_html=True)

def render_header():
    st.markdown("""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
            <h1 style="letter-spacing: 5px; font-size: 3.5rem; margin-bottom: 0;">[ i  am ]  |  A I M</h1>
            <p style="opacity: 0.6; font-size: 1.2rem;">Artificial Intelligenz matching</p>
        </div>
    """, unsafe_allow_html=True)

def render_beta_footer():
    st.markdown("""
        <div style="background-color: #F8F9FB; padding: 30px; border-radius: 8px; margin-top: 50px; text-align: center; border: 1px solid #EEEEEE;">
            <p style="font-size: 0.9rem; color: #666;"><b>Beta-Status:</b> Transparenz: AIM ist eine Dating bzw. Freundesuch-Website in Resonanz.
                Dein Vibe Key ist dein einziger Zugang.</p>
        </div>
    """, unsafe_allow_html=True)