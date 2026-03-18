import streamlit as st
import style
import db_handler

# WICHTIG: Erst initialisieren, dann rendern!
style.init_global_state() 
style.apply_custom_style()
style.render_nav() # Jetzt findet er das Attribut garantiert!

st.set_page_config(page_title="Admin | [i am] | AIM", layout="wide")
style.apply_custom_style()
style.render_nav()
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
style.render_header()

# Check ob Admin-Rechte (einfacher Check über Session oder Email)
user = st.session_state.get('user_data', {})
if user.get('email') == "mcv@iam-aim.com": # Dein Admin-Account [cite: 2025-11-08]
    st.title("⚙ Admin-Zentrale")
    
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profiles")
    total = cur.fetchone()[0]
    cur.close(); conn.close()
    
    st.metric("Registrierte Seelen", total)
    st.write("Hier folgen bald die Steuerungselemente für den Batch-Worker.")
else:
    st.error("Zugriff verweigert. Nur für Core-Entwickler.")

style.render_beta_footer()