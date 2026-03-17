import streamlit as st

def apply_custom_style(): 
    st.markdown(
        """
        <style>
        /* 1. GLOBALE TYPO & FARBEN */
        .stApp { background-color: #FFFFFF !important; color: #111111 !important; }
        
        /* Überschriften über den Eingabefeldern abdunkeln */
        .stMarkdown p, label, .stWidgetLabel p {
            color: #111111 !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        /* 2. NAVIGATION: Horizontal ausgerichtet & Gleiche Abstände */
        div.stButton > button {
            width: 100% !important;
            background-color: #F0F2F6 !important;
            color: #333333 !important;
            border: 1px solid #CCCCCC !important;
            border-radius: 4px !important;
            padding: 10px 0 !important;
        }
        
        .active-nav-btn button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #000000 !important;
        }

        /* 3. DROPDOWNS: Dunkelgrau statt Schwarz */
        div[data-baseweb="select"] > div {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        div[data-baseweb="popover"] ul {
            background-color: #333333 !important;
        }

        /* 4. SLIDER: Schwarze Linie, Grüner Bereich */
        /* Die Grundlinie */
        div[data-baseweb="slider"] > div {
            background-color: #000000 !important;
        }
        /* Der aktive Range-Bereich */
        div[data-baseweb="slider"] > div > div {
            background-color: #00FF00 !important; /* Resonanz-Grün */
            background-image: none !important;
        }
        /* Die Knöpfe */
        div[role="slider"] {
            background-color: #000000 !important;
            border: 2px solid #00FF00 !important;
        }

        /* 5. ABSTÄNDE */
        .main-unit { margin-bottom: 40px; }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_nav():
    """Navigations-Buttons mit exakt gleichem horizontalem Abstand."""
    current_menu = st.session_state.get('menu', "Manifesto erstellen")
    # 5 Spalten mit exakt gleicher Breite (1:1:1:1:1)
    cols = st.columns([1, 1, 1, 1, 1])
    
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
                if ".py" in target: st.switch_page(f"pages/{target}")
                else: st.switch_page("app.py")
            st.markdown('</div>', unsafe_allow_html=True)

def render_header():
    # Logo + Subline als Einheit mit definiertem Bottom-Margin
    st.markdown("""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
            <h1 style="letter-spacing: 5px; font-size: 3rem; margin-bottom: 0;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6; font-size: 1.1rem;">Authentic Intelligence Mate</p>
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