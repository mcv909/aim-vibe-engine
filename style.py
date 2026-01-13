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
    """Zeigt den Header an. Nutzt Text-Fallback für den Clean-Look (v0.4.2)."""
    img_blur = None
    img_clear = None
    
    # Versuch, die Bilder zu laden
    try:
        img_blur = get_base64_of_bin_file("header_blurry.png")
        img_clear = get_base64_of_bin_file("header_clear.png")
    except Exception:
        # Wenn Bilder fehlen, bleiben die Variablen None -> wir zeigen Text
        pass

    if img_blur and img_clear:
        # Der komplexe Bilder-Look (nur wenn Dateien existieren)
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="data:image/png;base64,{img_clear}" style="width: 250px; border-radius: 10px;">
            </div>
        """, unsafe_allow_html=True)
    else:
        # CLEAN LOOK (v0.4.2): Zentrierter Text ohne Schnickschnack
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px; margin-bottom: 50px;">
                <h1 style="font-weight: 200; letter-spacing: 8px; font-size: 3rem; color: #FAFAFA !important;">
                    [ I  A  M ]  |  A I M
                </h1>
                <p style="opacity: 0.5; font-size: 1.1rem; letter-spacing: 2px;">
                    AI-Matching basierend auf Resonanz, nicht auf Checklisten.
                </p>
            </div>
            """, unsafe_allow_html=True
        )