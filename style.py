import streamlit as st

# Zentrales CD (Corporate Design) [cite: 2026-01-17]
CD_WEISS = "#FFFFFF"
CD_SCHWARZ = "#111111"
CD_GRAU_HELL = "#F8F9FB"
CD_NEON_GRUEN = "#39FF14" # Die Farbe der Resonanz

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
    """Stellt sicher, dass alle Variablen in der Matrix existieren, egal auf welcher Seite man startet."""
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
        /* 1. STREAMLIT UI OVERRIDE */
        header {{ visibility: hidden !important; height: 0px !important; }}
        .stAppHeader {{ display: none !important; }}
        [data-testid="stSidebarNav"] {{ display: none !important; }}

        /* 2. GLOBALE FARBEN */
        .stApp {{ background-color: {CD_WEISS} !important; color: {CD_SCHWARZ} !important; }}
        
        /* Überschriften knackig schwarz */
        .stMarkdown p, label, .stWidgetLabel p {{
            color: {CD_SCHWARZ} !important;
            font-weight: 700 !important;
        }}

        /* 3. INPUTS: Weißer Hintergrund, schwarze Typo */
        .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div {{
            background-color: {CD_WEISS} !important;
            color: {CD_SCHWARZ} !important;
            border: 1px solid #CCCCCC !important;
        }}

        /* 4. BUTTONS: Navigation & Primary */
        div.stButton > button {{
            width: 100% !important;
            background-color: {CD_GRAU_HELL} !important;
            color: {CD_SCHWARZ} !important;
            border: 1px solid #DDDDDD !important;
            padding: 12px !important;
            font-weight: 600 !important;
        }}
        
        /* Primäre Buttons (Login/Sichern): Weiß auf Schwarz */
        button[kind="primary"], button[kind="primaryFormSubmit"] {{
            background-color: {CD_SCHWARZ} !important;
            color: {CD_WEISS} !important;
            border: 1px solid {CD_SCHWARZ} !important;
        }}

        .active-nav-btn button {{
            background-color: {CD_SCHWARZ} !important;
            color: {CD_WEISS} !important;
        }}

        /* 5. SLIDER: Weißer Hintergrund, schwarze Schiene, NEONGRÜN aktiv */
        div[data-baseweb="slider"] > div {{ background-color: {CD_WEISS} !important; }}
        div[data-baseweb="slider"] > div > div:first-child {{ background-color: {CD_SCHWARZ} !important; }}
        div[data-baseweb="slider"] > div > div > div {{
            background-color: {CD_NEON_GRUEN} !important;
            background-image: none !important;
        }}
        div[role="slider"] {{
            background-color: {CD_SCHWARZ} !important;
            border: 2px solid {CD_NEON_GRUEN} !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    # Aktuellen Dateinamen ermitteln
    try:
        current_page = st.source_code_path.split("/")[-1]
    except:
        current_page = "app.py"
        
    cols = st.columns(5)
    menus = [
        ("✎ Manifesto", "Manifesto erstellen", "app.py"),
        ("⚿ Login", "Login", "app.py"),
        ("◬ Resonanz", "Resonanz", "qa.py"),
        ("ⓘ Über AIM", "Über AIM", "about.py"),
        ("⚙ Admin", "Admin", "admin.py")
    ]
    
    for i, (label, menu_val, target_file) in enumerate(menus):
        with cols[i]:
            # Aktiven Status erkennen (entweder über die Datei oder den Menu-Status)
            is_active = (st.session_state.menu == menu_val and current_page == "app.py") or \
                        (current_page == target_file and target_file != "app.py")
            
            st.markdown(f'<div class="{"active-nav-btn" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{i}"):
                st.session_state.menu = menu_val # Modus setzen
                
                # Navigation entscheiden
                if target_file == "app.py":
                    if current_page == "app.py":
                        st.rerun() # Auf der Hauptseite nur neu laden
                    else:
                        st.switch_page("app.py") # Von Unterseite zurück zur Hauptseite
                else:
                    st.switch_page(f"pages/{target_file}")
            st.markdown('</div>', unsafe_allow_html=True)

def render_header():
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
            <h1 style="letter-spacing: 5px; font-size: 3.5rem; margin-bottom: 0;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6; font-size: 1.2rem;">Authentic Intelligence Mate</p>
        </div>
    """, unsafe_allow_html=True)

def render_beta_footer():
    st.markdown(f"""
        <div style="background-color: {CD_GRAU_HELL}; padding: 30px; border-radius: 8px; margin-top: 50px; text-align: center; border: 1px solid #EEEEEE;">
            <p style="font-size: 0.9rem; color: #666;"><b>Beta-Status:</b> AIM ist ein Experiment in Resonanz. Dein Vibe Key ist dein einziger Zugang. [cite: 2026-01-18]</p>
        </div>
    """, unsafe_allow_html=True)