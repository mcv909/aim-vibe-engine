import streamlit as st
# HIER DIE KORREKTUR: apply_custom_style statt set_page_style
from style import apply_custom_style, render_header

def main():
    st.set_page_config(page_title="Q&A | [i am] | AIM", layout="wide")
    apply_custom_style()
    render_header()

    st.title("💡 Fragen & Resonanzen")
    st.markdown("---")

    qa_data = [
        {
            "q": "Was ist das hier genau? Was passiert hier?",
            "a": "AIM ist kein klassisches Dating-Portal. Es ist eine Resonanz-Engine. Wir nutzen hochdimensionale Vektoren (KI-Embeddings), um Menschen auf Basis ihrer inneren Werte, Musikgeschmäcker und Lebenseinstellungen zusammenzubringen, statt nur oberflächliche Checklisten abzuarbeiten."
        },
        {
            "q": "Was ist der Unterschied zu anderen Partnersuchwebsites?",
            "a": "Wir verzichten auf endlose Filter-Marathons. Das Herzstück ist dein Manifesto – ein freier Text, der deine 'Digitale DNA' repräsentiert. Unsere KI analysiert die Schwingung deiner Worte und sucht nach passenden Gegenstücken im morphogenetischen Feld des Netzwerks."
        },
        {
            "q": "Kosten?",
            "a": "Für unsere Pioniere (die ersten 2.000 User) bleibt der Account lebenslang beitragsfrei. Wir nennen das Pionier-Privileg. Für alle späteren Anmeldungen wird eine Gebühr fällig, die aktuell noch intern kalkuliert wird."
        },
        {
            "q": "Was ist, wenn ich meinen Telegram-Account nicht mehr habe?",
            "a": "Telegram dient als dein Identitäts-Anker. Ohne Zugriff auf deinen Handle ist eine Wiederherstellung aus Sicherheitsgründen aktuell nicht möglich. Dein Account ist fest mit deiner Telegram-ID verknüpft."
        },
        {
            "q": "Was ist, wenn ich meinen Key für die Site verliere?",
            "a": "Dein Vibe-Key ist der Schlüssel zu deinen verschlüsselten Daten. Da wir den Key selbst nicht im Klartext speichern (Zero-Knowledge-Prinzip), können wir dein Profil bei Verlust nicht 'entsperren'. Du kannst dir den Key aber jederzeit erneut über unseren Telegram-Bot zuschicken lassen, solange du Zugriff auf dein Telegram-Konto hast."
        },
        {
            "q": "Kann ich meinen Text anpassen/verändern?",
            "a": "Absolut. Resonanz ist fluide. Du kannst dich jederzeit mit deinem Key einloggen und dein Manifesto aktualisieren, um deinen Vektor neu auszurichten."
        },
        {
            "q": "Wer bekommt meine Daten?",
            "a": "Niemand außer deinem potenziellen Match. Dein Manifesto wird verschlüsselt gespeichert. Selbst wir als Administratoren sehen nur Vektoren (Zahlenreihen), keine Klartexte. Erst bei einem Match wird dein gewählter Kontaktweg (Telegram/Signal) für die andere Person sichtbar."
        },
        {
            "q": "Was passiert bei einem Match?",
            "a": "Wenn das System eine hohe Resonanz (Similarity-Score) feststellt, wird euch das Profil des jeweils anderen angezeigt. Ihr erhaltet dann den hinterlegten Kontaktweg, um die Konversation in der realen Welt fortzusetzen."
        },
        {
            "q": "An wen kann ich mich wenden, wenn ich Hilfe benötige?",
            "a": "Das Team (Ivee, Jens, Marc) ist erreichbar unter: support@iam-aim.com. Bitte beachte, dass wir ein Beta-Projekt sind und die Antwortzeiten variieren können."
        },
        {
            "q": "Kann ich meine KI einen Text über mich schreiben lassen?",
            "a": "Technisch möglich, aber nicht ratsam. Eine KI schreibt oft das, was sie denkt, was man hören will. Wahre Resonanz entsteht durch Authentizität. Ein selbst geschriebenes Manifesto liefert statistisch gesehen die deutlich besseren Matches."
        },
        {
            "q": "Was genau soll in dem 'Manifesto' stehen?",
            "a": "Alles, was dich ausmacht: Werte, Leidenschaften (Techno!), Ansichten zu Gerechtigkeit oder dein Lifestyle. Stell es dir wie ein hochauflösendes Bild vor: Je mehr Details du gibst, desto schärfer wird dein Matching-Profil."
        },
        {
            "q": "Gibt es Garantien für Matches?",
            "a": "Nein. Wir garantieren lediglich die mathematische Wahrscheinlichkeit einer hohen Übereinstimmung. Die Chemie beim ersten Date in der echten Welt können wir (noch) nicht berechnen."
        },
        {
            "q": "Was passiert, wenn niemand matcht?",
            "a": "Dann ist das Feld vielleicht gerade nicht in deiner Schwingung. Du kannst deinen Suchradius erweitern oder dein Manifesto verfeinern, um andere Resonanzpunkte zu setzen."
        },
        {
            "q": "Wie kann ich meine Chance auf Matches vergrößern?",
            "a": "Schreibe ausführlich und ehrlich. Ein kurzes Manifesto führt zu einem 'verpixelten' Matching. Je mehr qualitative Anker du wirfst, desto eher bleibt jemand daran hängen."
        },
        {
            "q": "Jemand hat Zugriff auf meinen Account hier, was kann ich tun?",
            "a": "Nutze sofort die Löschfunktion über unseren Telegram-Bot. Da Telegram dein Sicherheitsanker ist, kannst du deinen Datensatz dort jederzeit per Befehl unwiderruflich aus der Datenbank entfernen."
        }
    ]

    for item in qa_data:
        st.markdown(f"**{item['q']}**")
        st.markdown(f"<p style='font-size: 0.9rem; color: #AAAAAA; margin-bottom: 25px;'>{item['a']}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()