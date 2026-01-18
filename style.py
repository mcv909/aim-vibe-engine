import streamlit as st

def apply_custom_style():
    """Konfiguriert das Layout und das visuelle Branding von AIM [cite: 2026-01-18]."""
    
    # Seite konfigurieren (Muss der erste Streamlit-Befehl sein!)
    st.set_page_config(
        page_title="[ i am ] | AIM",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS für das "hart cleane" Dark-Mode Design
    st.markdown("""
        <style>
        /* Hintergrund und Grundfarben */
        .stApp {
            background-color: #0D1B2E;
            color: #E0E1DD;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1B263B;
            border-right: 1px solid #415A77;
        }
        
        /* Überschriften-Design */
        h1, h2, h3 {
            font-family: 'Courier New', Courier, monospace;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #778DA9;
        }
        
        /* Buttons (Der rote Action-Button) */
        div.stButton > button:first-child {
            background-color: #E63946;
            color: white;
            border: none;
            border-radius: 0px;
            padding: 0.6rem 2rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:first-child:hover {
            background-color: #D62828;
            box-shadow: 0 0 15px rgba(230, 57, 70, 0.4);
        }

        /* Input Felder */
        .stTextInput > div > div > input {
            background-color: #1B263B;
            color: #E0E1DD;
            border: 1px solid #415A77;
        }
        </style>
    """, unsafe_allow_html=True)