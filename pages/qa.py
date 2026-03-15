import streamlit as st
import style

def main():
    # 1. Page Config & Styles
    st.set_page_config(page_title="Q&A | [i am] | AIM", layout="wide")
    style.apply_custom_style()
    style.render_nav() # WICHTIG: Die zentrale Navigation [cite: 2026-03-12]
    style.render_header()

    st.markdown("<h2 style='text-align: center;'>◬ Fragen & Resonanzen</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. Bereinigte QA-Daten (Ohne Telegram) [cite: 2026-03-12]
    qa_data = [
        {
            "q": "Was ist das hier genau?",
            "a": "AIM ist eine Resonanz-Engine. Wir nutzen hochdimensionale Vektoren, um Menschen auf Basis ihrer inneren Werte und Lebenseinstellungen zusammenzubringen, statt nur oberflächliche Checklisten abzuarbeiten."
        },
        {
            "q": "Wie funktioniert das Matching im 1536-D Raum?"
            "a": "Stell dir vor, dein Text wird in 1536 verschiedene Facetten oder 'Bedeutungs-Räume' zerlegt. Dabei hat jeder Raum eine spezifische mathematische Wertung. **Die Logik dahinter:** * **Präzision:** Je mehr Text du lieferst, desto feiner und schärfer werden diese Räume ausgeleuchtet. * **Muster:** AIM erstellt daraus eine mathematische 'Perlenkette' deines Vibes. * **Resonanz:** Wenn die Hardfacts (Alter, Ort etc.) passen, legen wir deine Kette über alle anderen. Wir suchen nicht nach gleichen Wörtern, sondern berechnen die mathematische Übereinstimmung der Muster. Das ist echte Resonanz im 1536-dimensionalen Raum."
        },
        {
            "q": "Was ist der Unterschied zu anderen Portalen?",
            "a": "Das Herzstück ist dein Manifesto – ein freier Text, der deine 'Digitale DNA' repräsentiert. Unsere KI analysiert die Schwingung deiner Worte im 1536-D Raum." 
        },
        {
            "q": "Was passiert, wenn ich meinen Vibe-Key verliere?",
            "a": "Dein Vibe-Key ist der einzige Schlüssel zu deinen verschlüsselten Daten. Da wir Zero-Knowledge fahren, können wir dein Profil bei Verlust nicht entsperren. Dein Passwort ist dein Schutzschild."
        },
        {
            "q": "Wer bekommt meine Daten?",
            "a": "Niemand außer deinem potenziellen Match. Dein Manifesto wird verschlüsselt gespeichert. Selbst wir als Admins sehen nur Vektoren (Zahlenreihen), keine Klartexte." 
        },
        {
            "q": "Was passiert bei einem Match?",
            "a": "Bei hoher Resonanz (Similarity-Score) wird euch das Profil des anderen angezeigt. Ihr erhaltet dann den gewählten Kontaktweg, um euch in der realen Welt kennenzulernen."
        },
        {
            "q": "Wie kann ich meine Chance auf Matches vergrößern?",
            "a": "Ein kurzes Manifesto führt zu einem 'verpixelten' Matching. Je mehr qualitative Anker du wirfst, desto präziser kann AIM die Resonanz berechnen."        }
    ]

    for item in qa_data:
        st.markdown(f"**{item['q']}**")
        st.markdown(f"<p style='font-size: 0.95rem; color: #555555; margin-bottom: 25px;'>{item['a']}</p>", unsafe_allow_html=True)

    style.render_beta_footer()

if __name__ == "__main__":
    main()