import numpy as np
import db_handler
import psycopg2.extras
import json

def parse_vector(vector_data):
    """Wandelt den DB-String oder die Liste sicher in ein Numpy-Array um [cite: 2026-03-28]."""
    if isinstance(vector_data, str):
        # Entfernt die eckigen Klammern und splittet bei Kommas
        return np.fromstring(vector_data.strip('[]'), sep=',')
    return np.array(vector_data)

def calculate_cosine_similarity(vec1, vec2):
    """Berechnet die mathematische Resonanz zwischen zwei Vektoren [cite: 2026-02-07]."""
    v1 = parse_vector(vec1)
    v2 = parse_vector(vec2)
    
    # Check auf Dimensionen (Sollte 1536 sein) [cite: 2026-02-07]
    if v1.shape[0] != 1536 or v2.shape[0] != 1536:
        raise ValueError(f"Dimensionen passen nicht: {v1.shape[0]} vs {v2.shape[0]}")
        
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def run_resonance_test():
    print("🛰️  AIM RESONANZ-ANALYSE: Starte Abgleich...")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # 1. Marc (Admin) laden [cite: 2026-03-27]
        cur.execute("""
            SELECT p.email, mv.embedding 
            FROM profiles p 
            JOIN manifesto_vectors mv ON p.id = mv.profile_id 
            WHERE p.email = 'mcv@iam-aim.com' AND mv.embedding IS NOT NULL;
        """)
        admin = cur.fetchone()
        
        if not admin:
            print("❌ Admin-Profil nicht gefunden oder noch nicht vektorisiert!")
            return

        print(f"👤 Referenz-Profil: {admin['email']} geladen.")

        # 2. Andere Profile zum Vergleich [cite: 2026-03-27]
        cur.execute("""
            SELECT p.email, mv.embedding 
            FROM profiles p 
            JOIN manifesto_vectors mv ON p.id = mv.profile_id 
            WHERE p.email != 'mcv@iam-aim.com' AND mv.embedding IS NOT NULL;
        """)
        others = cur.fetchall()

        print("-" * 60)
        print(f"{'TEST-PROFIL':<25} | {'SCORE':<10} | {'STATUS'}")
        print("-" * 60)

        for user in others:
            try:
                score = calculate_cosine_similarity(admin['embedding'], user['embedding'])
                # Bewertungsschwellen [cite: 2025-12-30]
                status = "🔥 MATCH" if score > 0.85 else "🧊 FAIL"
                print(f"{user['email']:<25} | {score:.4f}     | {status}")
            except Exception as e:
                print(f"{user['email']:<25} | Fehler: {e}")

    except Exception as e:
        print(f"💥 Kritischer Fehler: {e}")
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    run_resonance_test()