import psycopg2
import psycopg2.extras
from psycopg2 import extensions, errors
import os
import json
import numpy as np
from dotenv import load_dotenv
import security 

load_dotenv()

# DB-Verbindung aus der .env
DB_NAME = os.getenv("DB_NAME", "aim_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

_VECTOR_OID = None

def register_vector_type(conn):
    """Registriert den pgvector-Typ global [cite: 2026-03-28]."""
    global _VECTOR_OID
    if _VECTOR_OID is None:
        cur = conn.cursor()
        cur.execute("SELECT oid FROM pg_type WHERE typname = 'vector';")
        res = cur.fetchone()
        if res:
            _VECTOR_OID = res[0]
            def cast_vector(value, cur):
                if value is None: return None
                return np.fromstring(value.strip('[]'), sep=',')
            
            VECTOR = extensions.new_type((_VECTOR_OID,), "VECTOR", cast_vector)
            extensions.register_type(VECTOR)
        cur.close()

def get_connection():
    """Zentrale Verbindungsstelle inkl. Typ-Registrierung [cite: 2026-03-12]."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    register_vector_type(conn) # Dies wandelt DB-Strings in Numpy-Floats [cite: 2026-03-28]
    return conn

def init_db():
    """Initialisiert die Matrix-Struktur [cite: 2026-02-03]."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                identity INT, search_for INT, age INT, height INT, stature_id INT, 
                coords JSONB, u_age_min INTEGER, u_age_max INTEGER,
                u_height_min INTEGER, u_height_max INTEGER, radius INTEGER DEFAULT 50,
                is_ukrainian BOOLEAN DEFAULT FALSE, is_email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT FALSE, 
                is_testuser BOOLEAN DEFAULT FALSE,
                key_hash TEXT, messenger_contact TEXT,
                verification_token UUID DEFAULT gen_random_uuid(),
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manifesto_vectors (
                profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
                manifesto_user TEXT,
                manifesto_enc TEXT,
                embedding vector(1536)
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()
        try:
        # Das Gedächtnis für bereits versendete Benachrichtigungen [cite: 2026-04-04]
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notified_matches (
                user_a UUID REFERENCES profiles(id) ON DELETE CASCADE,
                user_b UUID REFERENCES profiles(id) ON DELETE CASCADE,
                first_matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_score FLOAT,
                PRIMARY KEY (user_a, user_b)
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"DB-Init Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()

# ... (Hier folgen deine restlichen Funktionen wie save_profile_atomic, etc. 
# die nun alle die korrekte get_connection() nutzen)

def save_profile_atomic(data, manifesto_raw, vibe_key):
    conn = get_connection()
    cur = conn.cursor()
    is_test = data['email'].endswith('@iam-aim.com')
    try:
        # Wir verschlüsseln für den User-Login symmetrisch [cite: 2026-01-18]
        enc_manifesto = security.encrypt_data(manifesto_raw, vibe_key)
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None

        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, stature_id, 
                coords, is_ukrainian, key_hash, messenger_contact,
                u_age_min, u_age_max, u_height_min, u_height_max, radius, is_testuser
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, height = EXCLUDED.height, coords = EXCLUDED.coords,
                messenger_contact = EXCLUDED.messenger_contact, radius = EXCLUDED.radius,
                u_age_min = EXCLUDED.u_age_min, u_age_max = EXCLUDED.u_age_max,
                u_height_min = EXCLUDED.u_height_min, u_height_max = EXCLUDED.u_height_max,
                last_interaction = CURRENT_TIMESTAMP
            RETURNING id, verification_token;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], data['stature_id'], 
            coords_json, data.get('is_ukrainian', False), data.get('key_hash'),
            data.get('messenger_contact'), data.get('u_age_min'), data.get('u_age_max'),
            data.get('u_height_min'), data.get('u_height_max'), data.get('radius'), is_test
        ))
        p_id, v_token = cur.fetchone()

        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_enc)
            VALUES (%s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET manifesto_enc = EXCLUDED.manifesto_enc;
        """, (p_id, enc_manifesto))

        conn.commit()
        return v_token, "needs_verification"
    except Exception as e:
        conn.rollback()
        return None, f"System-Error: {str(e)}"
    finally:
        cur.close(); conn.close()

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
    conn = get_connection()
    # KORREKTUR: RealDictCursor statt RealDictRow [cite: 2026-03-15]
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    try:
        cur.execute("""
            SELECT p.*, mv.manifesto_enc as manifesto_text 
            FROM profiles p 
            LEFT JOIN manifesto_vectors mv ON p.id = mv.profile_id 
            WHERE p.email = %s
        """, (email,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()

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
    # KORREKTUR: Zugriff über psycopg2.extras fixen [cite: 2026-03-15]
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT DISTINCT ON (profile_id) id, profile_id, encrypted_manifesto 
            FROM embedding_queue 
            WHERE status = 'pending' 
            ORDER BY profile_id, created_at DESC;
        """)
        return cur.fetchall()
    finally:
        cur.close(); conn.close()

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

def get_user_manifesto_by_id(profile_id):
    """Holt das mit dem User-Vibe-Key verschlüsselte Manifesto."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT manifesto_user FROM manifesto_vectors WHERE profile_id = %s;", (profile_id,))
        res = cur.fetchone()
        return res[0] if res else None
    except Exception as e:
        print(f"DB-Fehler beim Laden des Manifestos: {e}")
        return None
    finally:
        cur.close(); conn.close()