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
    
    Dein Manifesto wurde sicher verschlüsselt übertragen.
    Klicke bitte auf den Link, um deine E-Mail zu bestätigen und dein Profil live zu schalten:
    
    {activation_link}
    
    Sobald du verifiziert bist, verortet AIM deinen Vibe mehrfach im 1536-D Raum.
    
    Viel Erfolg!
    Dein AIM (AI matching)
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

def generate_match_insights(scores):
    """
    Erstellt qualitative Hinweise basierend auf den Layer-Scores.
    scores: dict { 'sw': 0.92, 'sv': 0.45, ... }
    """
    insights = []
    
    # Grundwerte
    if scores['sw'] > 0.90:
        insights.append("Euer moralischer Kompass schlägt fast identisch aus – ein sehr tiefes Fundament.")
    
    # Kommunikation
    if scores['sk'] < 0.50:
        insights.append("Eure Art zu kommunizieren unterscheidet sich stark. Das könnte Reibung erzeugen, aber auch neue Perspektiven eröffnen.")
    elif scores['sk'] > 0.85:
        insights.append("Ihr sprecht dieselbe Sprache – Ironie und Zwischentöne werden wahrscheinlich sofort verstanden.")
        
    # Vibe
    if 0.40 <= scores['sv'] < 0.60:
        insights.append("In eurem Energie-Level seid ihr unterschiedlich, was für eine gute Balance zwischen Aktion und Ruhe sorgen kann.")

    return "\n".join(insights)