import streamlit as st

def set_page_style():
    """Setzt das globale CSS (Clean Layout, Fokus auf Tooltips & Validierung)."""
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF; color: #222222; }
        
        /* Akzentfarben: Dunkelblau für alles Operative */
        :root { --primary-color: #1B263B; }
        
        /* Tooltip Icon Style */
        .stTooltipIcon {
            color: #1B263B !important;
        }

        /* Felder einheitlich gestalten */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
            border: 2px solid #E0E0E0 !important;
            border-radius: 0px !important;
            color: #222 !important;
        }
        
        /* Der EINZIG ROTE Button */
        div.stButton > button {
            background-color: #FF4B4B !important;
            color: #FFFFFF !important;
            border: none !important;
            padding: 20px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            width: 100% !important;
            border-radius: 0px !important;
            letter-spacing: 2px;
        }

        /* Build-Hint & Status */
        .build-hint {
            font-family: 'Courier New', Courier, monospace;
            color: #1b5e20;
            font-size: 0.75rem;
            text-align: center;
            margin-top: -60px;
            margin-bottom: 40px;
        }

        /* Mona Lisa Boxen Alignment */
        .visual-anchor { display: flex; flex-direction: column; gap: 20px; margin-top: 10px; }
        .m-box { display: flex; align-items: flex-start; gap: 15px; height: 100px; }
        .m-img { width: 100px; height: 100px; overflow: hidden; border: 1px solid #EEE; flex-shrink: 0; }
        .m-img img { width: 100%; height: 100%; object-fit: cover; filter: grayscale(100%); }
        .img-low img { filter: grayscale(100%) blur(8px) contrast(200%); }
        .m-skeleton { flex-grow: 1; background-image: repeating-linear-gradient(to bottom, #E0E0E0, #E0E0E0 12px, transparent 12px, transparent 22px); }
        .sk-low { height: 34px; width: 40%; }
        .sk-high { height: 100%; width: 90%; }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_header():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 40px; margin-bottom: 70px; width: 100%;">
            <h1 style="font-weight: 900; letter-spacing: 12px; font-size: 5rem; line-height: 1; margin: 0 auto;">
                [ I  A  M ]  |  A I M
            </h1>
            <div style="max-width: 720px; margin: 15px auto 0 auto;">
                <p style="opacity: 0.4; font-size: 1.1rem; letter-spacing: 3.5px; text-transform: uppercase; text-align: justify; text-align-last: justify;">
                    AI-Matching basierend auf Resonanz, nicht auf Checklisten.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def render_visual_anchor():
    st.markdown("""
        <div class="visual-anchor">
            <div class="m-box">
                <div class="m-img img-low"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/157px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"></div>
                <div class="m-skeleton sk-low"></div>
            </div>
            <div class="m-box">
                <div class="m-img"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/157px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"></div>
                <div class="m-skeleton sk-high"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)