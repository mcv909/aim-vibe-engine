import streamlit as st
import style

st.set_page_config(page_title="Impressum | [i am] | AIM", layout="wide")
style.init_global_state()
style.apply_custom_style()
style.render_nav()
style.render_header()

st.markdown("### ⚖ Impressum")
st.markdown("""
#### Angaben gemäß § 5 TMG
**Betreiber:** Marc Chrsitian Vietor  
Lindenallee 20
19029 Lützow

#### Kontakt
**E-Mail: mcv@iam-aim.com  
**Web:** https://www.deepl.com/en/translator/q/de/an+deiner+Seite/en/at+your+side/f3a5613c

#### Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV
Marc Christian Vietor 
Lindenallee 20
19209 Lützow

#### Haftungsausschluss
Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für die Inhalte externer Links. Für den Inhalt der verlinkten Seiten sind ausschließlich deren Betreiber verantwortlich.
""")

style.render_beta_footer()