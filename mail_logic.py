import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_activation_mail(receiver_email, token):
    # Authentifizierungs-Daten aus der .env
    auth_user = os.getenv("MAIL_SENDER") # mcv@iam-aim.com
    auth_pass = os.getenv("MAIL_PASSWORD")
    
    # Der Alias, der beim User angezeigt wird [cite: 2026-03-12]
    display_from = "aktivierung@iam-aim.com"
    
    # Der Aktivierungslink (IP/Domain anpassen!) [cite: 2026-03-08]
    activation_link = f"http://91.98.23.22/?token={token}" 

    msg = MIMEMultipart()
    # Hier setzen wir den Alias und einen schönen Anzeigenamen [cite: 2026-03-12]
    msg['From'] = f"AIM | Aktivierung <{display_from}>"
    msg['To'] = receiver_email
    msg['Subject'] = "Aktiviere deinen Vibe-Check"

    body = f"""
    Moin! 
    
    Dein Manifesto wurde sicher verschlüsselt übertragen. [cite: 2026-01-18]
    Klicke bitte auf den Link, um deine E-Mail zu bestätigen und dein Profil live zu schalten:
    
    {activation_link}
    
    Sobald du verifiziert bist, verortet AIM deinen Vibe im 1536-D Raum. [cite: 2026-02-07]
    
    Viel Erfolg!
    Dein AIM (Authentic Intelligence Mate)
    """
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(auth_user, auth_pass) # Login mit mcv@ [cite: 2026-03-12]
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP-Fehler: {e}")
        return False