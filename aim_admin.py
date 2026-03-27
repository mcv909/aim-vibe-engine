import os
import subprocess
import shutil
import re
import platform
import smtplib
import numpy as np
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv

# Unsere Module
import db_handler

load_dotenv()

def print_header(title):
    print("\n" + "="*60)
    print(f"🛰️  {title.upper()}")
    print("="*60)

def get_server_stats():
    """Prüft Uptime, Disk und Last Login (Cross-Platform Mac/Linux)."""
    print_header("Server & Infrastruktur")
    
    # 1. Disk Space
    total, used, free = shutil.disk_usage("/")
    print(f"💾 DISK: {used//(2**30)}GB genutzt / {free//(2**30)}GB frei (Gesamt: {total//(2**30)}GB)")
    
    # 2. Uptime Fix für Mac/Linux [cite: 2026-02-03]
    try:
        if platform.system() == "Darwin": # MacAir
            uptime = subprocess.check_output(['uptime']).decode('utf-8').strip()
        else: # Hetzner (Linux)
            uptime = subprocess.check_output(['uptime', '-p']).decode('utf-8').strip()
        print(f"🕒 UPTIME: {uptime}")
    except Exception:
        print("🕒 UPTIME: Konnte nicht ermittelt werden.")
    
    # 3. Last Login
    try:
        last_log = subprocess.check_output(['last', '-n', '1']).decode('utf-8').split('\n')[0]
        print(f"👤 LAST LOGIN: {last_log}")
    except:
        print("👤 LAST LOGIN: Keine Daten.")

def check_security_logs():
    """Sucht nach fehlgeschlagenen Logins (Nur auf Linux sinnvoll)."""
    if platform.system() == "Darwin":
        print("\n🔒 SECURITY: SSH-Audit auf Mac übersprungen.")
        return

    print_header("Security Audit (Hacker-Radar)")
    try:
        # Check SSH Fehlversuche [cite: 2026-01-18]
        cmd = "grep 'Failed password' /var/log/auth.log | wc -l"
        failed = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        print(f"🛡️ SSH FEHLVERSUCHE: {failed} Einträge in /var/log/auth.log")
    except:
        print("⚠️ SECURITY: Zugriff auf auth.log verweigert (root benötigt).")

def scan_streamlit_logs():
    """Filtert Rauschen aus den Streamlit-Logs [cite: 2026-03-12]."""
    print_header("Streamlit Log-Analyse (Signal vs. Rauschen)")
    log_file = "streamlit.log"
    
    if not os.path.exists(log_file):
        print("ℹ️ Keine streamlit.log gefunden.")
        return

    # Relevante Fehler-Keywords [cite: 2026-02-03]
    error_patterns = [r"Traceback", r"Exception:", r"AttributeError:", r"psycopg2\..*Error", r"OpenAIError"]
    noise = ["GatherUsageStats", "Connection reset by peer", "Broken pipe"]

    found_errors = 0
    with open(log_file, "r") as f:
        lines = f.readlines()
        for line in lines[-200:]: # Letzte 200 Zeilen
            if any(re.search(p, line) for p in error_patterns):
                if not any(n in line for n in noise):
                    print(f"🚨 KRITISCH: {line.strip()}")
                    found_errors += 1
    
    if found_errors == 0:
        print("✨ Keine relevanten Fehler im Log-Fenster.")

def check_matrix_stats():
    """Der klassische Matrix-Report (V1) [cite: 2026-03-27]."""
    print_header("Matrix & Resonanz Status")
    try:
        conn = db_handler.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Profile & Vektoren [cite: 2026-02-07]
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_email_verified = true) as verified
            FROM profiles;
        """)
        stats = cur.fetchone()
        
        cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE embedding IS NOT NULL;")
        vecs = cur.fetchone()[0]

        print(f"👥 Profile gesamt:      {stats['total']}")
        print(f"📧 Verifiziert:         {stats['verified']}")
        print(f"✨ Vektorisierte DNA:   {vecs}")
        
        # Vektor-Integrität L2-Norm [cite: 2026-02-07]
        cur.execute("SELECT embedding FROM manifesto_vectors WHERE embedding IS NOT NULL LIMIT 1;")
        sample = cur.fetchone()
        if sample:
            vec = np.array(sample['embedding'])
            print(f"🔢 Vektor-Check: $1536$ Dim | $L2$-Norm: {np.linalg.norm(vec):.4f}")

        cur.close(); conn.close()
    except Exception as e:
        print(f"❌ MATRIX-FEHLER: {e}")

def troubleshoot_user(email):
    """Gezielte Diagnose für Bugfixing [cite: 2026-03-12]."""
    print_header(f"Diagnose: {email}")
    try:
        conn = db_handler.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM profiles WHERE email = %s;", (email,))
        user = cur.fetchone()

        if not user:
            print(f"❌ User '{email}' nicht gefunden.")
        else:
            print(f"✅ Profil {str(user['id'])[:8]}... aktiv.")
            print(f"📧 Verifiziert: {'JA' if user['is_email_verified'] else 'NEIN'}")
            # Check Vektor
            cur.execute("SELECT embedding FROM manifesto_vectors WHERE profile_id = %s;", (user['id'],))
            vec = cur.fetchone()
            print(f"🧬 DNA-Vektor:  {'BERECHNET' if vec and vec['embedding'] is not None else 'FEHLT'}")
        cur.close(); conn.close()
    except Exception as e:
        print(f"❌ TROUBLESHOOT-FEHLER: {e}")

if __name__ == "__main__":
    import sys
    get_server_stats()
    
    if len(sys.argv) > 1:
        troubleshoot_user(sys.argv[1])
    else:
        check_security_logs()
        scan_streamlit_logs()
        check_matrix_stats()
    
    print("\n✅ Admin-Check beendet.")