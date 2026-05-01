import psycopg2
import psycopg2.extras
from psycopg2 import extensions
import os
import json
import numpy as np
from dotenv import load_dotenv
import security 

load_dotenv()

# DB-Konfiguration
DB_NAME = os.getenv("DB_NAME", "aim_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

_VECTOR_OID = None

def register_vector_type(conn):
    """Registriert den pgvector-Typ global für Numpy-Konvertierung."""
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
    """Zentrale Verbindung inkl. Typ-Casting."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    register_vector_type(conn)
    return conn

def init_db():
    """Initialisiert die gesamte Matrix-Struktur inkl. Match-Gedächtnis."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 1. Profiles (Basisdaten)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                identity INT, search_for INT, age INT, height INT,
                coords JSONB, u_age_min INTEGER, u_age_max INTEGER,
                u_height_min INTEGER, u_height_max INTEGER, radius INTEGER DEFAULT 50,
                is_email_verified BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT FALSE,
                key_hash TEXT, messenger_contact TEXT,
                verification_token UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Manifesto-Vektoren (Hybride Verschlüsselung)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manifesto_vectors (
                profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
                manifesto_user TEXT,   -- AES (für User-Login) [cite: 2026-03-15]
                manifesto_enc TEXT,    -- RSA (für Worker) [cite: 2026-03-04]
                embedding vector(1536) -- Die mathematische DNA [cite: 2026-02-07]
            );
        """)

        # 3. Notified Matches (Dubletten-Schutz)
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
        conn.rollback()
        print(f"DB-Init Fehler: {e}")
    finally:
        cur.close(); conn.close()

def save_profile_atomic(data, manifesto_raw, pub_key, v_key):
    """Zentraler Speicherprozess inkl. doppelter Verschlüsselung."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Verschlüsselungsschichten
        user_enc = security.encrypt_data(manifesto_raw, v_key) if v_key else None
        worker_enc = security.encrypt_for_worker(manifesto_raw, pub_key) if pub_key else None
        coords_json = json.dumps(data.get('coords')) if data.get('coords') else None

        # 1. Profile speichern/updaten
        cur.execute("""
            INSERT INTO profiles (
                email, identity, search_for, age, height, coords, 
                key_hash, messenger_contact, u_age_min, u_age_max, 
                u_height_min, u_height_max, radius
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                age = EXCLUDED.age, height = EXCLUDED.height, coords = EXCLUDED.coords,
                identity = EXCLUDED.identity, search_for = EXCLUDED.search_for,
                u_age_min = EXCLUDED.u_age_min, u_age_max = EXCLUDED.u_age_max,
                u_height_min = EXCLUDED.u_height_min, u_height_max = EXCLUDED.u_height_max,
                radius = EXCLUDED.radius
            RETURNING id, verification_token;
        """, (
            data['email'], data['identity'], data['search_for'], 
            data['age'], data['height'], coords_json, 
            data.get('key_hash'), data.get('messenger_contact'),
            data['u_age_min'], data['u_age_max'], 
            data['u_height_min'], data['u_height_max'], data['radius']
        ))
        p_id, v_token = cur.fetchone()

        # 2. Manifesto-Layer speichern
        cur.execute("""
            INSERT INTO manifesto_vectors (profile_id, manifesto_user, manifesto_enc)
            VALUES (%s, %s, %s)
            ON CONFLICT (profile_id) DO UPDATE SET 
                manifesto_user = COALESCE(EXCLUDED.manifesto_user, manifesto_vectors.manifesto_user),
                manifesto_enc = EXCLUDED.manifesto_enc;
        """, (p_id, user_enc, worker_enc))

        conn.commit()
        return v_token, "needs_verification"
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        cur.close(); conn.close()

def get_profile_by_email(email):
    """Lädt das Profil inkl. User-Manifesto für den Login."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    try:
        cur.execute("""
            SELECT p.*, mv.manifesto_user as enc_manifesto 
            FROM profiles p 
            LEFT JOIN manifesto_vectors mv ON p.id = mv.profile_id 
            WHERE p.email = %s
        """, (email,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()

def verify_email_by_token(token):
    """Verifiziert die E-Mail und gibt die ID zurück."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE profiles SET is_email_verified = TRUE WHERE verification_token = %s RETURNING id;", (token,))
        res = cur.fetchone()
        conn.commit()
        return (True, res[0]) if res else (False, None)
    except:
        conn.rollback(); return False, None
    finally:
        cur.close(); conn.close()

def update_user_status(user_id, new_status):
    """Aktualisiert den Match-Status eines Users [cite: 2026-04-06]."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE profiles SET match_status = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Fehler beim Status-Update: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_user_manifesto_by_id(user_id):
    """
    Spezifischer Abruf für den Editor. 
    Hinweis: Nutzt 'manifesto_user' entsprechend deiner get_profile_by_email Logik.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT manifesto_user FROM manifesto_vectors WHERE profile_id = %s", (user_id,))
        res = cur.fetchone()
        return res[0] if res else None
    finally:
        cur.close(); conn.close()

def update_user_status(user_id, new_status):
    """Aktualisiert den Match-Status (searching, focusing, paused) in der DB."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE profiles SET match_status = %s WHERE id = %s", (new_status, user_id))
        conn.commit()
    except Exception as e:
        print(f"❌ Fehler beim Status-Update: {e}")
        conn.rollback()
    finally:
        cur.close(); conn.close()

def get_user_count():
    """Gibt die Anzahl der registrierten Profile in der Postgres-DB zurück."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM profiles;")
        count = cur.fetchone()[0]
        return count
    except Exception as e:
        print(f"Datenbank-Zählfehler: {e}")
        return 0
    finally:
        cur.close()
        conn.close()