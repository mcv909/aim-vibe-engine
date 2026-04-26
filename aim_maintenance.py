import os
import subprocess
from datetime import datetime
import db_handler

def run_backup():
    """Erstellt ein außerplanmäßiges Backup der gesamten AiM-Datenbank."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_aim_db_{timestamp}.sql"
    
    print(f"📦 Starte Sicherungslauf: {backup_file}...")
    try:
        # Nutzt pg_dump für eine vollständige Sicherung
        env = os.environ.copy()
        # Stelle sicher, dass DB_PASS in der Shell/Env gesetzt ist
        subprocess.run([
            "pg_dump", "-h", "localhost", "-U", "postgres", "-d", "aim_db", "-f", backup_file
        ], check=True)
        print(f"✅ Backup erfolgreich erstellt.")
        return True
    except Exception as e:
        print(f"❌ Backup fehlgeschlagen: {e}")
        return False

def start_waschmaschine():
    """Setzt die Vektoren zurück, um ein Re-Indexing zu erzwingen."""
    print("🧼 Starte Waschmaschine (Vektor-Reset)...")
    try:
        conn = db_handler.get_connection()
        cur = conn.cursor()
        
        # Wir löschen die Layer-Vektoren und den Zeitstempel
        cur.execute("""
            UPDATE manifesto_vectors SET 
                emb_werte = NULL, emb_vibe = NULL, 
                emb_offenheit = NULL, emb_komm = NULL, 
                last_matching_run = NULL;
        """)
        conn.commit()
        cur.close(); conn.close()
        print("✅ Alle Vektoren zurückgesetzt. Der Worker wird sie jetzt neu berechnen.")
    except Exception as e:
        print(f"❌ Fehler beim Reset: {e}")

if __name__ == "__main__":
    confirm = input("⚠️ Willst du wirklich alle Vektoren zurücksetzen? (y/n): ")
    if confirm.lower() == 'y':
        if run_backup():
            start_waschmaschine()
    else:
        print("Abgebrochen. Nichts passiert.")