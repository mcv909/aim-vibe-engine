import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from dotenv import load_dotenv # <--- DAS FEHLTE!
from security import decrypt_data # <--- Wichtig für load_db()

# HIER DIREKT LADEN
load_dotenv()

# DB-Verbindung aus der .env laden
DB_NAME = os.getenv("DB_NAME", "aim_db")
DB_USER = os.getenv("DB_USER", "postgres")
# WICHTIG: Prüfe in deiner .env ob es DB_PASS oder DB_PASSWORD heißt. 
# Dieser Fallback deckt beides ab:
DB_PASS = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def load_db():
    """Überbrückt die Postgres-DB für die app.py Matching-Logik."""
    conn = get_connection()
    # RealDictCursor sorgt dafür, dass wir Dictionaries wie früher bekommen
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM profiles WHERE is_active = true;")
        rows = cur.fetchall()
        # Wir müssen 'password_hash' zu 'key_hash' umbenennen für app.py Kompatibilität
        for row in rows:
            row['key_hash'] = row.pop('password_hash')
#            row['name'] = decrypt_data(row.pop('name_enc')) # Direkt entschlüsseln für UI
        return rows
    finally:
        cur.close()
        conn.close()

def get_user_count():
    """Gibt die Anzahl der aktiven Profile für das Dashboard zurück."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM profiles WHERE is_active = true;")
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()

def get_connection():
    """Baut die Verbindung zur Postgres-DB auf."""
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST, 
        port=DB_PORT
    )

def init_db():
    """Initialisiert die Datenbank-Struktur (Einmalig/Idempotent)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                telegram_id BIGINT UNIQUE,
                name_enc TEXT,
                contact_enc TEXT,
                password_hash TEXT,
                manifesto_enc TEXT,
                vector_string vector(1536),
                is_vectorized BOOLEAN DEFAULT false,
                is_active BOOLEAN DEFAULT true,
                early_adopter BOOLEAN DEFAULT false,
                coords JSONB,
                stature TEXT,
                target_stature TEXT[],
                radius INTEGER DEFAULT 50,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vector ON profiles USING hnsw (vector_string vector_cosine_ops);")
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def save_profile(data):
    """Speichert ein Profil und gibt die neue UUID zurück."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO profiles (
                telegram_id, name_enc, contact_enc, password_hash, 
                manifesto_enc, vibe_vector, coords, stature, 
                target_stature, radius, u_age, u_gender, 
                u_looking_for, u_age_min, u_age_max, u_intent, 
                u_height, u_target_height_min, u_target_height_max, 
                early_adopter
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id; 
        """, (
            data['telegram_id'], data['name_enc'], data['contact_enc'], data['password_hash'],
            data['manifesto_enc'], data['vector'], data.get('coords'), data['stature'],
            data['target_stature'], data['radius'], data['u_age'], data['u_gender'],
            data['u_looking_for'], data['u_age_min'], data['u_age_max'], data['u_intent'],
            data['u_height'], data['u_target_height_min'], data['u_target_height_max'],
            data.get('early_adopter', True)
        ))
        new_uuid = cur.fetchone()[0]
        conn.commit()
        return new_uuid
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

def add_to_embedding_queue(profile_id, encrypted_text):
    """Schiebt das RSA-verschlüsselte Manifesto in die Queue."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO embedding_queue (profile_id, encrypted_manifesto, status)
            VALUES (%s, %s, 'pending')
        """, (profile_id, encrypted_text))
        conn.commit()
        return True
    except Exception as e:
        print(f"Fehler in Queue-Eintrag: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_profile_by_telegram_id(tid):
    """Lädt ein Profil für den Login."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM profiles WHERE telegram_id = %s", (tid,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def delete_profile(telegram_id):
    """Löscht ein Profil und alle zugehörigen Matches unwiderruflich."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Erst die Matches löschen, damit es keinen Foreign-Key-Fehler gibt
        cur.execute("""
            DELETE FROM matches 
            WHERE user_a = (SELECT id FROM profiles WHERE telegram_id = %s) 
               OR user_b = (SELECT id FROM profiles WHERE telegram_id = %s)
        """, (telegram_id, telegram_id))
        
        # Dann das Profil selbst löschen
        cur.execute("DELETE FROM profiles WHERE telegram_id = %s", (telegram_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Datenbank-Fehler beim Löschen: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_match_count():
    """Gibt die Gesamtanzahl der gefundenen Resonanzen zurück."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM matches;")
        return cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
        
def save_feedback(user_id, rating, comment, match_id=None):
    """
    Speichert das User-Feedback zu einem Match oder der Systemqualität in die Datenbank.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO feedback (user_id, match_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (user_id, match_id, rating, comment))
        conn.commit()
        return True
    except Exception as e:
        # Fehlerlogging für die spätere Optimierung
        print(f"Fehler beim Speichern des Feedbacks: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def add_to_embedding_queue(profile_id, encrypted_text):
    """Schiebt ein verschlüsseltes Manifesto in die Warteschlange."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO embedding_queue (profile_id, encrypted_manifesto, status)
            VALUES (%s, %s, 'pending')
        """, (profile_id, encrypted_text))
        conn.commit()
        return True
    except Exception as e:
        print(f"Fehler in der Queue: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()