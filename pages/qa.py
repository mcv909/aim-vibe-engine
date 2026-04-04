import streamlit as st
import style # Greift auf style.py im Hauptverzeichnis zu
import db_handler

# WICHTIG: Erst initialisieren, dann rendern!
style.init_global_state() 
style.apply_custom_style()
style.render_nav() # Jetzt findet er das Attribut garantiert!

# aka Resonanz

def main():
    # 1. Page Config & Styles
    st.set_page_config(page_title="Q&A | [i am] | AiM", layout="wide")
    style.apply_custom_style()
    style.render_header()

    st.markdown("<h2 style='text-align: center;'>◬ Fragen & Resonanzen</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. Bereinigte QA-Daten (Ohne Telegram) [cite: 2026-03-12]
    qa_data = [
        {
            "q": "Was ist das hier genau?",
            "a": "AiM ist eine Resonanz-Engine. Wir nutzen hochdimensionale Vektoren, um Menschen auf Basis ihrer inneren Werte und Lebenseinstellungen zusammenzubringen, statt nur oberflächliche Checklisten abzuarbeiten."
        },
        {
            "q": "Wie funktioniert das Matching im 1536-D Raum?",
            "a": "Stell dir vor, dein Text wird in 1536 verschiedene Facetten oder 'Bedeutungs-Räume' zerlegt. Dabei hat jeder Raum eine spezifische mathematische Wertung. Die Logik dahinter: Präzision: Je mehr Text du lieferst, desto feiner und schärfer werden diese Räume ausgeleuchtet. Muster: AiM erstellt daraus eine mathematische 'Perlenkette' deines Vibes. Resonanz: Wenn die Hardfacts (Alter, Ort etc.) passen, legen wir deine Kette über alle anderen. Wir suchen nicht nach gleichen Wörtern, sondern berechnen die mathematische Übereinstimmung der Muster. Das ist echte Resonanz im 1536-dimensionalen Raum."
        },
            "q": "Funktioniert das wirklich?"
            "a": """Ja. Aber wir verlangen dir etwas ab: Einen langen Text der dich Beschreibt."
            Hier ist ein anonymisiertes Beispiel aus unseren Stresstests:
            Profil A: „...die meditative Einsamkeit des Waldes als Gegenpol zur technischen Präzision im Studio...
            Profil B: „...Suche die Dualität zwischen dunklen Clubs und der absoluten Stille des Morgengrauens...
            Ergebnis: Eine mathematische Resonanz von 0.92. Die KI hat erkannt, dass beide nicht nur „Techno“ mögen, sondern dieselbe psychologische Struktur (Ruhe vs. Ekstase) teilen."""
        {
            "q": "Was ist der Unterschied zu anderen Portalen?",
            "a": "1. Das Herzstück ist dein Manifesto – ein freier Text, der deine 'Digitale DNA' repräsentiert. Unsere lokale KI analysiert die Schwingung deiner Worte im 1536-D Raum.<br>"
            "2. Datenschutz ist Kern! Keiner kann deine Daten sehen - auch wir nicht. Es können Bspw. keine Profile verkauft werden ;)<br>"
            "3. Wir sind, aktuell, noch Kostenfrei! Sobald wir mehr Technik benötigen können wir das nicht aufrechterhalten ABER es wird nur einen einmaligen Beitrag sein - kein monatliches Schröpfen ;)"
        },
        {
            "q": "Was passiert, wenn ich meinen Vibe-Key verliere?",
            "a": "Dein Vibe-Key ist der einzige Schlüssel zu deinen verschlüsselten Daten. Da wir Zero-Knowledge fahren, können wir dein Profil bei Verlust nicht entsperren. Dein Passwort ist dein Schutzschild."
        },
        {
            "q": "Wer bekommt meine Daten?",
            "a": """Niemand!<br><br>
            Dein Manifesto wird verschlüsselt verarbeitet und dient rein der mathematischen Suche. 
            Selbst bei einer hohen Resonanz bekommt dein Match <b>nur deine Kontaktdaten</b> (Messenger/E-Mail), 
            aber niemals deinen Text.<br><br>
            Wir finden die Ähnlichkeit in 1536 Dimensionen – aber ihr dürft sie im echten Gespräch gemeinsam 
            herausfinden. Das ist der Kern von AiM: Wir liefern das Fundament, ihr die Story."""
        },
        {
            "q": "Was passiert bei einem Match?",
            "a": "Bei hoher Resonanz (Similarity-Score) werden euch die Kontaktdaten des Anderen angezeigt. Ihr erhaltet dann den gewählten Kontaktweg, um euch in der realen Welt kennenzulernen."
        },
        {
            "q": "Wie kann ich meine Chance auf Matches vergrößern?",
            "a": "Ein kurzes Manifesto führt zu einem 'verpixelten' Matching. Je mehr qualitative Anker du wirfst, desto präziser kann AiM die Resonanz berechnen."        
        },
        {
            "q": "Warum muss mein Manifesto so lang sein?"
            "a": "AIM arbeitet nicht mit Stichworten, sondern mit deiner „Digitalen DNA“. Erst ab ca. 500 Zeichen erreicht die mathematische Auflösung eine Qualität, die echte Resonanz von oberflächlichem Rauschen unterscheiden kann. Wir wollen, dass du nur Menschen triffst, die wirklich auf deiner Frequenz schwingen."
        },
        {
            "q": "Bekomme ich ständig dieselben Vorschläge?"
            "a": "Nein. Unser System besitzt ein „Match-Gedächtnis“. [cite: 2026-04-04] Sobald eine Resonanz festgestellt wurde, wird diese Information sicher gespeichert. Du wirst niemals doppelt über dasselbe Match benachrichtigt, selbst wenn wir unsere KI im Hintergrund optimieren."
        }
    ]

    for item in qa_data:
        st.markdown(f"**{item['q']}**")
        st.markdown(f"<p style='font-size: 0.95rem; color: #555555; margin-bottom: 25px;'>{item['a']}</p>", unsafe_allow_html=True)

    style.render_beta_footer()

if __name__ == "__main__":
    main()