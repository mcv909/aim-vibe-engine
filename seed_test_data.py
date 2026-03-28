import os
import json
import uuid
import db_handler
import security
from dotenv import load_dotenv

load_dotenv()

def seed_matrix():
    print("🚀 Starte kontrollierte DNA-Injektion...")
    pub_key = os.getenv("WORKER_PUBLIC_KEY")
    
    test_profiles = [
        {
            "name": "Marc (Admin)",
            "email": "mcv@iam-aim.com",
            "manifesto": "Ich liebe Techno, Gerechtigkeit und komplexe IT-Projekte. Ich bin fast 50 und suche echte Tiefe.",
            "data": {"age": 49, "identity": 1, "search_for": 2, "height": 180, "u_age_min": 30, "u_age_max": 55, "radius": 100, "u_height_min": 150, "u_height_max": 200, "is_ukrainian": False},
            "v_key": "vibe123"
        },
        {
            "name": "Resonanz-Match",
            "email": "match@iam-aim.com",
            "manifesto": "Musik ist mein Leben, besonders elektronische Beats. Soziale Gerechtigkeit ist mir wichtig. Suche jemanden für tiefgründige Gespräche.",
            "data": {"age": 45, "identity": 2, "search_for": 1, "height": 170, "u_age_min": 40, "u_age_max": 60, "radius": 50, "u_height_min": 170, "u_height_max": 195, "is_ukrainian": False},
            "v_key": "vibe456"
        },
        {
            "name": "Gegenpol",
            "email": "fail@iam-aim.com",
            "manifesto": "Ich mag Ruhe, Schlager und konservative Werte. Technik ist mir zu kompliziert. Ich lebe im Hier und Jetzt ohne große Planung.",
            "data": {"age": 25, "identity": 2, "search_for": 1, "height": 160, "u_age_min": 20, "u_age_max": 30, "radius": 20, "u_height_min": 160, "u_height_max": 180, "is_ukrainian": False},
            "v_key": "vibe789"
        }
    ]

    for p in test_profiles:
        # 1. Profile Entry
        user_data = {
            'email': p['email'],
            'coords': {"lat": 50.1109, "lon": 8.6821}, # Frankfurt Area
            'key_hash': security.hash_key(p['v_key']),
            'messenger_contact': "@test_handle",
            **p['data']
        }
        
        # 2. Speicherung (Aktivierung wird hier simuliert/übersprungen)
        conn = db_handler.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO profiles (email, identity, search_for, age, height, coords, is_ukrainian, key_hash, messenger_contact, u_age_min, u_age_max, u_height_min, u_height_max, radius, is_email_verified, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, true)
                RETURNING id;
            """, (user_data['email'], user_data['identity'], user_data['search_for'], user_data['age'], user_data['height'], json.dumps(user_data['coords']), user_data['is_ukrainian'], user_data['key_hash'], user_data['messenger_contact'], user_data['u_age_min'], user_data['u_age_max'], user_data['u_height_min'], user_data['u_height_max'], user_data['radius']))
            p_id = cur.fetchone()[0]

            # 3. Manifesto Layer
            user_enc = security.encrypt_data(p['manifesto'], p['v_key'])
            worker_enc = security.encrypt_for_worker(p['manifesto'], pub_key)
            
            cur.execute("INSERT INTO manifesto_vectors (profile_id, manifesto_user, manifesto_enc) VALUES (%s, %s, %s)", (p_id, user_enc, worker_enc))
            conn.commit()
            print(f"✅ Profil {p['name']} injiziert.")
        except Exception as e:
            print(f"❌ Fehler bei {p['name']}: {e}")
            conn.rollback()
        finally:
            cur.close(); conn.close()

if __name__ == "__main__":
    seed_matrix()