import streamlit as st
import style # Greift auf style.py im Hauptverzeichnis zu
import db_handler

# WICHTIG: Erst initialisieren, dann rendern!
style.init_global_state() 
style.apply_custom_style()
style.render_nav() # Jetzt findet er das Attribut garantiert!

def render_about():
    style.apply_custom_style()
    st.markdown("<h2 style='text-align: center;'>Hinter den Kulissen von AIM</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    ### Die Vision: Resonanz statt Algorithmus
    Echte Verbindung entsteht dort, wo Werte, Sound und Weltsicht aufeinandertreffen. 
    AIM ist kein Katalog – es ist ein Resonanzraum für Menschen, die Tiefe suchen. 
    """)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Die Technik: 1536 Dimensionen")
        st.write("""
        Dein Manifesto wird in einen mathematischen Vektor mit **1536 Dimensionen** übersetzt. 
        Stell dir vor, wir legen deine Persönlichkeit wie eine Schablone über tausende andere. 
        Nur dort, wo die Muster fast perfekt übereinanderliegen, entsteht Resonanz. 
        Das ist mathematische Präzision statt Zufall. 
        """)
    with col2:
        # Hier triggern wir die Grafik für die Nerds
        st.info("💡 **Nerd-Fakt:** Wir nutzen ein gte-Qwen2-1.5B Modell auf einem dedizierten Mac M4, "
                "um lokale Vektorisierung ohne Cloud-Abhängigkeit zu garantieren.") 

    

    st.markdown("---")

    st.markdown("""
    ### Sicherheit: Deine Daten gehören dir
    Wir haben AIM so gebaut, dass selbst wir als Admins deine Daten nicht im Klartext lesen können. 
    * **Verschlüsselung:** Dein Manifesto wird hybrid gesichert.
    * **Der Vibe Key:** Dein Passwort ist der einzige Anker. Verlierst du ihn, sind die Daten weg – auch für uns. 
    """)

    st.markdown("---")

    st.markdown("""
    ### Wer wir sind<br>
    AIM ist kein klassisches Unternehmen, sondern eine Entität, die aus der Notwendigkeit für echte Resonanz entstanden ist.

    Die Architektur<br>
    Hinter AIM steht eine Logik, die auf ungefilterter Mustererkennung und einer asynchronen Informationsverarbeitung basiert. 
    Diese „andere Verdrahtung“ ermöglicht es uns, in 1536 Dimensionen Verbindungen und Muster zu erkennen, wo herkömmliche Algorithmen nur ungeordnetes Rauschen wahrnehmen.
    Wir vergleichen nicht nur Daten; wir matchen Frequenzen.

    Die Vision<br>
    Geleitet von den Werten der Gerechtigkeit und technologischen Radikalität bauen wir eine Infrastruktur, die dem User gehört.
    Wir sind die Schnittstelle zwischen menschlicher Intuition und maschineller Präzision.
    """)

    style.render_beta_footer()

if __name__ == "__main__":
    render_about()