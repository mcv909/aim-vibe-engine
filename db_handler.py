import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
import os
import json
from dotenv import load_dotenv
import security  # Wichtig: Das gesamte Modul importieren! [cite: 2026-03-03]

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
    """Lädt alle Profile und entschlüsselt die Basis-Daten für die Admin-Ansicht."""
    conn = get_connection()
    # Wir nutzen RealDictCursor, damit wir über Spaltennamen zugreifen können
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT id, telegram_id, name_enc, contact_enc, coords, 
                   u_age, u_gender, created_at 
            FROM profiles 
            ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        
        # Die Daten für die UI aufbereiten
        decrypted_profiles = []
        for row in rows:
            # Wir wandeln das Row-Objekt in ein normales Dict um
            p = dict(row)
            try:
                # Entschlüsselung der Basis-Daten
                p['name'] = security.decrypt_data(p['name_enc'])
                p['contact'] = security.decrypt_data(p['contact_enc'])
            except Exception as e:
                # Falls ein Key fehlt oder Daten korrupt sind
                p['name'] = "[Decryption Error]"
                p['contact'] = "[Hidden]"
                print(f"Admin-Ansicht Fehler für ID {p['id']}: {e}")
            
            decrypted_profiles.append(p)
            
        return decrypted_profiles
    except Exception as e:
        print(f"Fehler beim Laden der Admin-DB: {e}")
        return []
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
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )

def init_db():
    """Initialisiert die Datenbank-Struktur mit 1536 Dimensionen."""
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
                manifest_enc TEXT,
                vibe_vector vector(1536),
                is_vectorized BOOLEAN DEFAULT false,
                is_active BOOLEAN DEFAULT true,
                early_adopter BOOLEAN DEFAULT true,
                coords JSONB,
                stature TEXT,
                target_stature TEXT[],
                radius INTEGER DEFAULT 50,
                u_age INTEGER,
                u_gender TEXT,
                u_looking_for TEXT,
                u_age_min INTEGER,
                u_age_max INTEGER,
                u_intent TEXT,
                u_height INTEGER,
                u_target_height_min INTEGER,
                u_target_height_max INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vector ON profiles USING hnsw (vibe_vector vector_cosine_ops);")
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def save_profile_atomic(data, manifesto_raw):
    """
    Speichert das Profil und bereitet die Vektorisierung vor.
    Nutzt Email als Anker und trennt Hard-Facts von Vektoren. [cite: 2026-03-08]
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Koordinaten-Check (Wir bleiben bei JSONB für Hetzner)
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None
        
        # 2. Profil-UPSERT in 'profiles'
        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, stature_id, 
                coords, is_ukrainian, key_hash, last_seen
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age,
                height = EXCLUDED.height,
                stature_id = EXCLUDED.stature_id,
                coords = EXCLUDED.coords,
                last_seen = CURRENT_TIMESTAMP
            RETURNING id;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], data['stature_id'], 
            coords_json, data.get('is_ukrainian', False), data.get('key_hash')
        ))
        profile_id = cur.fetchone()[0]

        # 3. Manifesto & Queue (Verschlüsselung für den Worker)
        # Wir speichern den Text erst mal flach, bis der Vektor da ist.
        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_text)
            VALUES (%s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET manifesto_text = EXCLUDED.manifesto_text;
        """, (profile_id, manifesto_raw))

        # 4. Ab in die Queue für das gte-Qwen2-1.5B Modell [cite: 2026-02-07]
        # (Hier könntest du deine bestehende embedding_queue nutzen)
        
        conn.commit()
        return profile_id, "success"
    except Exception as e:
        conn.rollback()
        print(f"Fehler beim Speichern: {e}")
        return None, "system_error"
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

def get_profile_by_email(email):
    """Lädt ein Profil für den Login oder Abgleich via Email.""" [cite: 2026-03-08]
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM profiles WHERE email = %s", (email,))
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

def fetch_pending_jobs_latest_only():
    """Holt pro User nur den aktuellsten 'pending' Job."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # DISTINCT ON sorgt dafür, dass wir pro profile_id nur eine Zeile bekommen.
        # ORDER BY sorgt dafür, dass es die NEUESTE (DESC) ist. [cite: 2026-03-03]
        cur.execute("""
            SELECT DISTINCT ON (profile_id) id, profile_id, encrypted_manifesto 
            FROM embedding_queue 
            WHERE status = 'pending' 
            ORDER BY profile_id, created_at DESC;
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def finalize_vibe_vector(profile_id, vector):
    """Schreibt den 1536-D Vektor in die manifesto_vectors Tabelle.""" [cite: 2026-02-07]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE manifesto_vectors 
            SET embedding = %s 
            WHERE profile_id = %s
        """, (vector, profile_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Vektor-Finalisierung Fehler: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def mark_job_failed(job_id):
    """Markiert einen Job in der Queue als gescheitert."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE embedding_queue SET status = 'error' WHERE id = %s", (job_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()