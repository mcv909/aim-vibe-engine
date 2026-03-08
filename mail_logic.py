import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_activation_mail(user_email, token):
    """Versendet den Aktivierungslink via Google SMTP."""
    sender_email = "deine-mail@deine-domain.de" 
    mail_password = "dein-google-app-passwort" # In .env auslagern!
    
    # Der Link für das Frontend (Streamlit-URL)
    link = f"https://deine-aim-app.de/?token={token}"
    
    msg = MIMEMultipart()
    msg['From'] = f"AIM - Authentic Intelligence Mate <{sender_email}>"
    msg['To'] = user_email
    msg['Subject'] = "Aktivierung deines 1536-D Vibe-Profils" [cite: 2026-02-07]

    body = f"""
    Moin!
    
    Fast geschafft. Klicke auf den Link, um dein Profil zu verifizieren.
    Danach berechnet unser MacAir-Worker deine Resonanz im 1536-dimensionalen Raum. [cite: 2026-02-07, 2025-12-20]
    
    Link: {link}
    
    Wir freuen uns auf deinen Vibe.
    Dein AIM
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Mail-Fehler: {e}")
        return False