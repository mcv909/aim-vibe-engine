import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_activation_mail(user_email, token):
    """Versendet den Aktivierungslink via Google SMTP Relay."""
    sender_email = os.getenv("MAIL_SENDER", "vibe@iam-aim.com")
    mail_password = os.getenv("MAIL_PASSWORD") # Dein 16-stelliges App-Passwort
    
    # URL der App (z.B. https://iam-aim.com)
    base_url = os.getenv("APP_URL", "http://localhost:8501") 
    link = f"{base_url}/?token={token}"
    
    msg = MIMEMultipart()
    msg['From'] = f"AIM - Authentic Intelligence Mate <{sender_email}>"
    msg['To'] = user_email
    msg['Subject'] = "Aktivierung deines 1536-D Vibe-Profils"

    body = f"""
    Moin!
    
    Dein Vibe-Profil ist fast bereit. Klicke auf den Link, um deine E-Mail zu bestätigen:
    
    {link}
    
    Sobald du verifiziert bist, berechnet unser System deine Resonanz-Werte.
    
    Dein AIM
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, mail_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Mail-Fehler: {e}")
        return False