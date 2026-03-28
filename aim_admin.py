import os
import subprocess
import shutil
import re
import platform
import smtplib
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

def check_matrix_integrity():
    """Prüft, ob die DB-Struktur alle 14 DNA-Felder enthält [cite: 2026-02-03]."""
    print_header("DNA-Struktur Abgleich")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    
    # Liste der 14 erwarteten DNA-Kernfelder (plus technische Felder)
    expected_fields = [
        'email', 'identity', 'search_for', 'age', 'height', 'coords', 
        'u_age_min', 'u_age_max', 'u_height_min', 'u_height_max', 'radius',
        'key_hash', 'messenger_contact'
    ]
    
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles';")
    existing_fields = [row[0] for row in cur.fetchall()]
    
    missing = [f for f in expected_fields if f not in existing_fields]
    
    if not missing:
        print(f"✅ INTEGRITÄT: Alle DNA-Kernfelder ({len(expected_fields)}) in der Datenbank vorhanden.")
    else:
        print(f"❌ FEHLER: Fehlende Felder in 'profiles': {', '.join(missing)}")
    
    # Check Manifesto Layer [cite: 2026-03-15]
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'manifesto_vectors';")
    mv_fields = [row[0] for row in cur.fetchall()]
    if 'manifesto_user' in mv_fields and 'manifesto_enc' in mv_fields:
        print("✅ VERSCHLÜSSELUNG: AES- und RSA-Layer Spalten sind aktiv.")
    
    cur.close(); conn.close()

def get_matrix_stats():
    """Holt die harten Zahlen aus der Matrix [cite: 2026-03-27]."""
    print_header("Matrix Statistiken")
    try:
        conn = db_handler.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_email_verified = true) as verified,
                COUNT(*) FILTER (WHERE is_active = true) as active
            FROM profiles;
        """)
        p_stats = cur.fetchone()
        
        cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE embedding IS NOT NULL;")
        vec_count = cur.fetchone()[0]

        print(f"👥 Profile gesamt:      {p_stats['total']}")
        print(f"📧 E-Mail verifiziert:  {p_stats['verified']}")
        print(f"🟢 Aktiv im Matching:   {p_stats['active']}")
        print(f"✨ Vektorisierte DNA:   {vec_count}")
        
        if p_stats['total'] > 0:
            print("-" * 60)
            print("🏆 TESTDATEN-CHECK:")
            cur.execute("SELECT email, age, messenger_contact FROM profiles LIMIT 5;")
            for row in cur.fetchall():
                print(f"  👉 {row['email']} | Alter: {row['age']} | Kontakt: {row['messenger_contact']}")
        
        cur.close(); conn.close()
    except Exception as e:
        print(f"❌ STATS-FEHLER: {e}")

# ... (Hier die restlichen Funktionen: get_server_stats, scan_streamlit_logs etc. behalten)

if __name__ == "__main__":
    # 1. Server Check
    total, used, free = shutil.disk_usage("/")
    print_header("Server & Infrastruktur")
    print(f"💾 DISK: {used//(2**30)}GB genutzt / {free//(2**30)}GB frei")
    
    # 2. Integrität & Stats
    check_matrix_integrity()
    get_matrix_stats()
    
    # 3. Logs
    # scan_streamlit_logs() # Optional, falls log vorhanden
    
    print("\n✅ Admin-Check beendet.")