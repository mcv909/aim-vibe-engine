import streamlit as st

def set_page_style():
    """Wiederherstellung des hellen Produktions-Looks (v0.4.2 Style)."""
    st.markdown(
        """
        <style>
        /* Hintergrund & Basis-Text */
        .stApp {
            background-color: #FFFFFF;
            color: #262730;
        }
        /* Header & Headlines */
        h1, h2, h3 {
            color: #000000 !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 200;
            text-align: center;
        }
        /* Die graue Inhalts-Box (Card) */
        div[data-testid="stForm"], .beta-box {
            background-color: #F0F2F6;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #E6E9EF;
        }
        /* Input Felder weiß machen */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {
            background-color: white !important;
        }
        /* Beta-Footer Styling */
        .footer-box {
            background-color: #E9ECEF;
            padding: 20px;
            border-radius: 5px;
            margin-top: 50px;
            font-size: 0.9rem;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

def render_header():
    """Der minimalistische Text-Header der Prod."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px; margin-bottom: 20px;">
            <h1 style="letter-spacing: 5px;">[ I  A  M ]  |  A I M</h1>
            <p style="opacity: 0.6;">AI-Matching basierend auf Resonanz, nicht auf Checklisten.</p>
        </div>
        """, unsafe_allow_html=True
    )