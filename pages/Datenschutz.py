import streamlit as st
import style

st.set_page_config(page_title="Datenschutz | [i am] | AIM", layout="wide")
style.init_global_state()
style.apply_custom_style()
style.render_nav()
style.render_header()

st.markdown("### 🔒 Datenschutz & Transparenz")
st.markdown("""
AIM wurde nach dem Prinzip **'Security by Design'** entwickelt. Wir wollen keine Daten besitzen, wir wollen Resonanz ermöglichen.

#### 1. Zero-Knowledge-Architektur
* **Verschlüsselung:** Dein Manifesto wird mit deinem persönlichen **Vibe Key** (AES-256) verschlüsselt. [cite: 2026-01-18]
* **Schlüsselgewalt:** Nur du hältst den Key. Wir speichern lediglich einen Hashwert zur Verifizierung deines Logins. [cite: 2026-01-18]
* **Verlust:** Wenn du deinen Vibe Key verlierst, sind deine Daten für immer verloren. Wir haben keine Hintertür. [cite: 2026-01-18]

#### 2. Datenverarbeitung & Vektorisierung
* **Der 1536-D Raum:** Zur Berechnung der Resonanz wird dein Text in einen mathematischen Vektor mit 1536 Dimensionen übersetzt. [cite: 2026-02-07]
* **Temporäre Verarbeitung:** Der Text wird ausschließlich im isolierten Arbeitsspeicher (RAM) unseres lokalen Workers (Mac M4 Architektur) kurzzeitig entschlüsselt, um den Vektor zu erzeugen. Danach wird der Klartext sofort aus dem Speicher gelöscht. [cite: 2026-02-03]
* **Permanente Speicherung:** Dauerhaft gespeichert werden nur der verschlüsselte Blob und die anonyme Zahlenreihe des Vektors. [cite: 2026-02-07, 2026-03-04]

#### 3. Löschkonzept (Deadman-Ping)
* **Inaktivität:** Profile, die länger als ein Jahr inaktiv sind, werden automatisch gelöscht. [cite: 2026-01-18]
* **Manuelle Löschung:** Über den Telegram-Handle kannst du dein Profil jederzeit ohne Passwort löschen lassen (sofern verknüpft). [cite: 2026-01-18]
* **Ping-Intervall:** Wir senden alle 6 Monate einen Deadman-Ping. Erfolgt innerhalb von 4 Wochen keine Reaktion, wird der Datensatz unwiderruflich entfernt. [cite: 2026-01-18]
""")

style.render_beta_footer()