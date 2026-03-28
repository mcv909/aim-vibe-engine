import os
import smtplib
import shutil
import platform
import re
import numpy as np
import psycopg2.extras
from dotenv import load_dotenv

# Unsere Module
import db_handler

load_dotenv()

def print_header(title):
    print("\n" + "="*60)
    print(f"🛰️  {title.upper()}")
    print("="*60)

def send_admin_alert(subject, body):
    """Sendet eine Alarm-Mail an den Admin [cite: 2026-03-12]."""
    sender = os.getenv("MAIL_SENDER")
    pwd = os.getenv("MAIL_PASSWORD")
    receiver = "mcv@iam-aim.com"
    
    msg = f"Subject: {subject}\n\n{body}"
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, receiver, msg.encode('utf-8'))
        server.quit()
        print(f"✅ ALERT-MAIL gesendet an {receiver}")
    except Exception as e:
        print(f"❌ MAIL-FEHLER beim Senden des Alerts: {e}")

def get_server_stats():
    """Prüft Ressourcen und gibt bei Engpässen eine Warnung zurück."""
    print_header("Server & Infrastruktur")
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    print(f"💾 DISK: {used//(2**30)}GB genutzt / {free_gb}GB frei")
    
    # Kritischer Schwellenwert: 5 GB [cite: 2026-02-03]
    if free_gb < 5:
        return False, f"⚠️ Speicherplatz kritisch: Nur noch {free_gb}GB frei!"
    return True, None

def scan_streamlit_logs():
    """Scannt Logs und zählt kritische Fehler."""
    print_header("Streamlit Log-Analyse")
    log_file = "streamlit.log"
    if not os.path.exists(log_file):
        return 0

    error_patterns = [r"Traceback", r"Exception:", r"AttributeError:", r"psycopg2\..*Error"]
    noise = ["GatherUsageStats", "Connection reset by peer", "Broken pipe"]
    
    found_errors = 0
    with open(log_file, "r") as f:
        for line in f.readlines()[-200:]:
            if any(re.search(p, line) for p in error_patterns):
                if not any(n in line for n in noise):
                    print(f"🚨 KRITISCH: {line.strip()}")
                    found_errors += 1
    return found_errors

def check_matrix_stats():
    """Prüft die Erreichbarkeit der Datenbank."""
    print_header("Matrix Status")
    try:
        conn = db_handler.get_connection()
        conn.close()
        print("✅ DATABASE: Verbindung stabil.")
        return True
    except Exception as e:
        print(f"❌ DATABASE: Verbindung fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    issues = []
    
    # 1. Ressourcen-Check
    status, msg = get_server_stats()
    if not status:
        issues.append(msg)
        
    # 2. Log-Check
    log_errors = scan_streamlit_logs()
    if log_errors > 0:
        issues.append(f"Kritische Streamlit-Fehler gefunden: {log_errors} neue Einträge.")
        
    # 3. Datenbank-Check
    if not check_matrix_stats():
        issues.append("Datenbank-Verbindung konnte nicht hergestellt werden.")

    # 4. Alert-Versand bei Problemen
    if issues:
        alert_body = "Das AIM Command Center hat folgende Unregelmäßigkeiten festgestellt:\n\n" + "\n".join(issues)
        send_admin_alert("🛰️ AIM ALERT: System-Inkonsistenz erkannt", alert_body)
    else:
        print("\n✨ System-DNA stabil. Keine Alerts notwendig.")