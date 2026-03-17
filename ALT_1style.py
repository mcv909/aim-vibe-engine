import streamlit as st

def apply_custom_style(): 
    st.markdown(
        """
        <style>
        /* 1. HEADER & OVERLAY FIX: Entfernt den schwarzen Balken oben */
        header { visibility: hidden !important; height: 0px !important; }
        .stAppHeader { display: none !important; }
        
        /* 2. GLOBALE FARBPALETTE */
        .stApp { background-color: #FFFFFF !important; color: #111111 !important; }
        
        /* Überschriften: Schwarz und kräftig */
        .stMarkdown p, label, .stWidgetLabel p {
            color: #111111 !important;
            font-weight: 700 !important;
        }

        /* 3. INPUTS & DROPDOWNS: Weißer Hintergrund, schwarze Typo */
        .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #111111 !important;
            border: 1px solid #CCCCCC !important;
        }

        /* 4. BUTTONS: Einheitliches Design für Nav und Primary */
        div.stButton > button {
            width: 100% !important;
            background-color: #F8F9FB !important;
            color: #111111 !important;
            border: 1px solid #DDDDDD !important;
            padding: 10px !important;
            font-weight: 600 !important;
        }
        
        /* Fix für den Login-Button (Primary/Submit) */
        button[kind="primaryFormSubmit"], button[kind="primary"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #000000 !important;
        }

        .active-nav-btn button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
        }

        /* 5. SLIDER: Weißer Hintergrund, schwarze Schiene, neongrüner Fortschritt */
        div[data-baseweb="slider"] > div { background-color: #FFFFFF !important; }
        /* Schiene */
        div[data-baseweb="slider"] > div > div:first-child { background-color: #000000 !important; }
        /* Aktiver Bereich (Neon-Grün) */
        div[data-baseweb="slider"] > div > div > div {
            background-color: #39FF14 !important;
            background-image: none !important;
        }
        /* Knöpfe */
        div[role="slider"] {
            background-color: #000000 !important;
            border: 2px solid #39FF14 !important;
        }

        /* 6. RIBBON / STÖRER */
        .aim-ribbon {
            position: fixed;
            top: 40px;
            right: -40px;
            background-color: #ff4b4b;
            color: white;
            padding: 5px 45px;
            transform: rotate(45deg);
            z-index: 10000;
            font-weight: bold;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    current_menu = st.session_state.get('menu', "Manifesto erstellen")
    cols = st.columns(5) # Automatische Gleichverteilung
    menus = [
        ("✎ Manifesto", "Manifesto erstellen"),
        ("⚿ Login", "Login"),
        ("◬ Resonanz", "qa.py"),
        ("ⓘ Über AIM", "about.py"),
        ("⚙ Admin", "Admin")
    ]
    for i, (label, target) in enumerate(menus):
        with cols[i]:
            is_active = (current_menu == target)
            st.markdown(f'<div class="{"active-nav-btn" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{i}"):
                st.session_state.menu = target
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def render_header():
    # Logo und Subline als Block
    st.markdown("""
        <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
            <h1 style="letter-spacing: 5px; font-size: 3.5rem; margin-bottom: 0;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6; font-size: 1.2rem; font-weight: 300;">Authentic Intelligence Mate</p>
        </div>
    """, unsafe_allow_html=True)

def render_beta_footer():
    """Der fehlende Footer zur Abrundung der Matrix."""
    st.markdown("""
        <div style="background-color: #F8F9FB; padding: 40px; border-radius: 8px; margin-top: 60px; border: 1px solid #EEEEEE;">
            <p style="font-size: 0.9rem; color: #666; text-align: center;">
                <b>Beta-Status & Transparenz:</b> AIM ist die erste "Dating"/"Freunde suche" Seite in Resonanz. <br>
                Dein Vibe Key ist dein einziger Zugang.
            </p>
        </div>
    """, unsafe_allow_html=True)

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