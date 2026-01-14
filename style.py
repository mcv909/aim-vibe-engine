import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    """Hilfsfunktion, um Bilder in Base64 umzuwandeln."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

def set_page_style():
    """Setzt das globale CSS für die Seite (Prod-Layout: Weiß & Clean)."""
    st.markdown(
        """
        <style>
        /* Grundlayout (Produktions-Style) */
        .stApp {
            background-color: #FFFFFF;
            color: #222222;
        }
        
        /* Headline & Typo (Testseiten-Wucht mit Prod-Schnitt) */
        h1, h2, h3 {
            color: #000000 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-weight: 900 !important;
            letter-spacing: -1px;
        }

        /* Manifesto-Bereich (Das bin ich) */
        .stTextArea textarea {
            background-color: #FAFAFA !important;
            border: 2px solid #E0E0E0 !important;
            border-radius: 0px !important;
            color: #222 !important;
        }
        
        /* Eingabefelder */
        .stTextInput input {
            background-color: #FAFAFA !important;
            border: 2px solid #E0E0E0 !important;
            border-radius: 0px !important;
        }

        /* Buttons (AIM-Vibe) */
        div.stButton > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 20px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            width: 100% !important;
            border-radius: 0px !important;
            letter-spacing: 2px;
        }
        
        div.stButton > button:hover {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }

        /* Mona Lisa Boxen (Alignment) */
        .m-box {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            height: 100px;
            margin-bottom: 25px;
        }
        .m-img-container {
            width: 100px; height: 100px;
            overflow: hidden;
            border: 1px solid #EEE;
            flex-shrink: 0;
        }
        .m-img-container img { width: 100%; height: 100%; object-fit: cover; }
        .img-low img { filter: grayscale(100%) blur(8px) contrast(200%); }
        .img-high img { filter: grayscale(100%) contrast(110%); }

        /* Typo-Simulation (Skelett) */
        .m-skeleton {
            flex-grow: 1;
            background-image: repeating-linear-gradient(
                to bottom, #E0E0E0, #E0E0E0 12px, transparent 12px, transparent 22px
            );
        }
        .sk-low { height: 34px; width: 40%; }
        .sk-high { height: 100%; width: 90%; }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header():
    """Zentraler Header: Groß, Clean, Impact."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 60px; margin-bottom: 80px;">
            <h1 style="font-weight: 900; letter-spacing: 12px; font-size: 5rem; line-height: 1; margin-bottom: 20px;">
                [ I  A  M ]  |  A I M
            </h1>
            <p style="opacity: 0.4; font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase;">
                AI-Matching basierend auf Resonanz, nicht auf Checklisten.
            </p>
        </div>
        """, unsafe_allow_html=True
    )