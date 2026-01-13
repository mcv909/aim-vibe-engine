import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    """Hilfsfunktion, um Bilder in Base64 umzuwandeln."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_page_style():
    """Setzt das globale CSS für die Seite."""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117; /* Sehr dunkler Hintergrund */
            color: #FAFAFA; /* Heller Text */
        }
        h1, h2, h3 {
            color: #FF4B4B !important; /* Streamlit-Rot für Überschriften */
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 200;
        }
        .stTextInput > label, .stSelectbox > label, .stTextArea > label {
            color: #FAFAFA !important; /* Helle Labels für Eingabefelder */
        }
        /* Anpassung der Expander-Box */
        .streamlit-expanderHeader {
            background-color: #262730;
            color: #FAFAFA;
            border-radius: 5px;
        }
        /* Style für die Match-Boxen */
        .match-box {
            border: 1px solid #444;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            background-color: #1E1E1E;
        }
        .match-score { color: #FF4B4B; font-weight: bold; }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header():
    """Zeigt Text-Header an. Bilder werden nur geladen, wenn vorhanden."""
    try:
        img_blur = get_base64_of_bin_file("header_blurry.png")
        img_clear = get_base64_of_bin_file("header_clear.png")
        # ... (dein bisheriger Bilder-Code) ...
    except FileNotFoundError:
        # CLEAN LOOK: Wenn Bilder fehlen, nur der Text wie in PROD
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
                <h1 style="font-weight: 200; letter-spacing: 5px;">[ I  A  M ]  |  A I M</h1>
                <p style="opacity: 0.6;">AI-Matching basierend auf Resonanz, nicht auf Checklisten.</p>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 30px;">
            <div style="position: relative; width: 80%; max-width: 600px;">
                <img src="data:image/png;base64,{img_blur}" 
                     style="width: 100%; border-radius: 15px; opacity: 0.4; position: absolute; top: 0; left: 0; z-index: 1;">
                
                <div style="position: relative; z-index: 2; padding: 20px; text-align: center;">
                    <img src="data:image/png;base64,{img_clear}" 
                         style="width: 60%; border-radius: 10px; box-shadow: 0 0 20px rgba(255, 75, 75, 0.5);">
                    <h3 style="margin-top: 20px; color: #FAFAFA !important; text-shadow: 1px 1px 2px #000;">
                        Der Unterschied zwischen Rauschen und Resonanz ist Mathematik.
                    </h3>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )