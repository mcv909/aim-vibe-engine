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
    """Lädt Profile für die Admin-Ansicht (E-Mail basiert)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT id, email, coords, age, identity, is_ukrainian, 
                   is_email_verified, is_active, created_at 
            FROM profiles 
            ORDER BY created_at DESC;
        """)
        return cur.fetchall()
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
    """Initialisiert die neue Business-Struktur (Email-First)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                identity INT, 
                search_for INT, 
                age INT,
                height INT, 
                stature_id INT, 
                coords JSONB, -- Deine stabile JSONB-Lösung
                
                -- Hard-Filter Parameter
                u_age_min INTEGER,
                u_age_max INTEGER,
                u_height_min INTEGER,
                u_height_max INTEGER,
                radius INTEGER DEFAULT 50,
                
                -- Status & Security
                is_ukrainian BOOLEAN DEFAULT FALSE, --
                is_email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT FALSE,
                key_hash TEXT, --
                messenger_contact TEXT, -- Optional
                verification_token UUID DEFAULT gen_random_uuid(),
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Für 12-Monats-Ping
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Die Vektor-Tabelle bleibt für die Performance separat
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manifesto_vectors (
                profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
                manifesto_enc TEXT, -- Verschlüsselt für MacAir-Worker
                embedding vector(1536) -- gte-Qwen2-1.5B
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()

def save_profile_atomic(data, manifesto_raw, pub_key):
    """Speichert Profil und bereitet Vektorisierung nach Mail-Check vor."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Manifesto verschlüsseln (Nur der User/Worker kann es lesen) [cite: 2026-01-18]
        enc_manifesto = security.encrypt_for_worker(manifesto_raw, pub_key)
        
        # 2. Koordinaten-Logik (Stabile JSONB Lösung)
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None

        # 3. Profil-UPSERT
        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, stature_id, 
                coords, is_ukrainian, key_hash, messenger_contact,
                last_interaction
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age,
                height = EXCLUDED.height,
                stature_id = EXCLUDED.stature_id,
                coords = EXCLUDED.coords,
                is_ukrainian = EXCLUDED.is_ukrainian,
                messenger_contact = EXCLUDED.messenger_contact,
                last_interaction = CURRENT_TIMESTAMP
            RETURNING id, verification_token;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], data['stature_id'], 
            coords_json, data.get('is_ukrainian', False), data.get('key_hash'),
            data.get('messenger_contact')
        ))
        p_id, v_token = cur.fetchone()

        # 4. Manifesto verschlüsselt ablegen
        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_enc)
            VALUES (%s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET manifesto_enc = EXCLUDED.manifesto_enc;
        """, (p_id, enc_manifesto))

        conn.commit()
        return v_token, "needs_verification"
    except Exception as e:
        conn.rollback()
        print(f"Fehler: {e}")
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
    """Lädt ein Profil für den Login oder Abgleich via Email.""" # [cite: 2026-03-08]
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM profiles WHERE email = %s", (email,))
        return cur.fetchone()
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
    """Schreibt den 1536-D Vektor in die manifesto_vectors Tabelle.""" # [cite: 2026-02-07]
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

def verify_email_by_token(token):
    """Setzt is_email_verified auf True und bereitet Vektorisierung vor."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Profil anhand des Tokens finden und verifizieren
        cur.execute("""
            UPDATE profiles 
            SET is_email_verified = TRUE, last_interaction = CURRENT_TIMESTAMP
            WHERE verification_token = %s
            RETURNING id;
        """, (token,))
        result = cur.fetchone()
        
        if result:
            profile_id = result[0]
            # 2. Hier könntest du jetzt ein Signal an die Queue senden, 
            # dass der MacAir-Worker loslegen darf. [cite: 2025-12-20, 2026-03-04]
            conn.commit()
            return True, profile_id
        return False, None
    except Exception as e:
        conn.rollback()
        return False, None
    finally:
        cur.close()
        conn.close()