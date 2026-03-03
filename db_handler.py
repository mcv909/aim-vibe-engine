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
    """Baut die Verbindung zur Postgres-DB auf."""
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASS, 
        host=DB_HOST, 
        port=DB_PORT
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

def save_profile_atomic(data, manifesto_raw, pub_key):
    """Speichert Profil und Queue-Eintrag in einer einzigen Transaktion."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Hybride Verschlüsselung erzeugen
        enc_manifesto = security.encrypt_for_worker(manifesto_raw, pub_key)
        
        # 2. Daten für DB vorbereiten
        raw_coords = data.get('coords') or data.get('coords_json')
        coords_json = json.dumps(raw_coords) if raw_coords else None
        ts_data = data.get('target_stature', [])
        ts_list = [s.strip() for s in ts_data.split(',')] if isinstance(ts_data, str) else ts_data

        # 3. Profil-UPSERT (In die 'profiles' Tabelle!) [cite: 2026-03-03]
        cur.execute("""
            INSERT INTO profiles (
                telegram_id, name_enc, contact_enc, password_hash, 
                manifesto_enc, coords, stature, target_stature, 
                radius, u_age, u_gender, u_looking_for, 
                u_age_min, u_age_max, u_intent, u_height, 
                u_target_height_min, u_target_height_max, early_adopter
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (telegram_id) DO UPDATE SET
                name_enc = EXCLUDED.name_enc,
                contact_enc = EXCLUDED.contact_enc,
                manifesto_enc = EXCLUDED.manifesto_enc,
                coords = EXCLUDED.coords,
                stature = EXCLUDED.stature,
                target_stature = EXCLUDED.target_stature,
                u_age = EXCLUDED.u_age,
                u_intent = EXCLUDED.u_intent
            RETURNING id;
        """, (
            data['telegram_id'], data['name_enc'], data['contact_enc'], data['password_hash'],
            enc_manifesto, coords_json, data['stature'], ts_list,
            data['radius'], data['u_age'], data['u_gender'], data['u_looking_for'],
            data['u_age_min'], data['u_age_max'], data['u_intent'], data['u_height'],
            data['u_target_height_min'], data['u_target_height_max'], data.get('early_adopter', True)
        ))
        p_id = cur.fetchone()[0]

        # 4. Queue-Eintrag (Stumpfes INSERT für die Historie) [cite: 2026-03-03]
        cur.execute("""
            INSERT INTO embedding_queue (profile_id, encrypted_manifesto, status)
            VALUES (%s, %s, 'pending');
        """, (p_id, enc_manifesto))

        conn.commit()
        return p_id, "success"

    except errors.UniqueViolation as e:
        conn.rollback()
        err_msg = str(e)
        if "telegram_id" in err_msg: return None, "duplicate_id"
        if "contact_enc" in err_msg: return None, "duplicate_contact"
        return None, "duplicate_entry"
    except Exception as e:
        conn.rollback()
        print(f"Atomarer Fehler: {e}")
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

def fetch_pending_jobs():
    """Holt die aktuellsten pending Jobs aus der Queue (Latest-Only)."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=db_handler.RealDictCursor) # Für lesbare Dicts
    try:
        # Der magische SQL-Befehl: 
        # 1. Nimm nur 'pending'
        # 2. Gruppiere nach profile_id (DISTINCT ON)
        # 3. Sortiere so, dass der neueste (DESC) oben liegt
        cur.execute("""
            SELECT DISTINCT ON (profile_id) 
                id, 
                profile_id, 
                encrypted_manifesto 
            FROM embedding_queue 
            WHERE status = 'pending' 
            ORDER BY profile_id, created_at DESC;
        """)
        jobs = cur.fetchall()
        
        # Markiere die abgeholten Jobs direkt als 'processing'
        if jobs:
            job_ids = [job['id'] for job in jobs]
            cur.execute("UPDATE embedding_queue SET status = 'processing' WHERE id = ANY(%s)", (job_ids,))
            conn.commit()
            
        return jobs
    except Exception as e:
        print(f"Fehler beim Job-Fetch: {e}")
        conn.rollback()
        return []
    finally:
        cur.close()
        conn.close()