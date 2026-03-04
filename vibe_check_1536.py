import db_handler
import numpy as np

def check_vector_integrity():
    print("--- AIM Vektor-Check ---")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    
    try:
        # Wir holen uns das neueste vektorisierte Profil
        cur.execute("""
            SELECT id, telegram_id, vibe_vector 
            FROM profiles 
            WHERE is_vectorized = TRUE 
            ORDER BY created_at DESC LIMIT 1;
        """)
        profile = cur.fetchone()
        
        if not profile:
            print("❌ Kein vektorisiertes Profil gefunden. Läuft der Worker?")
            return

        p_id, t_id, vector = profile
        
        # 1. Dimensions-Check
        dim = len(vector)
        print(f"✅ Profil {t_id} gefunden.")
        print(f"📊 Dimensionen: {dim}")
        
        if dim == 1536:
            print("✨ Perfekt! 1536 Dimensionen erkannt.")
        else:
            print(f"⚠️ Warnung: Erwartet 1536, aber {dim} erhalten.")

        # 2. Mathematische Stichprobe
        vec_np = np.array(vector)
        norm = np.linalg.norm(vec_np)
        print(f"🔢 Vektor-Norm (L2): {norm:.4f}") # Sollte bei gte-Modellen oft nahe 1 sein
        print(f"📌 Stichprobe (erste 3 Werte): {vector[:3]}")

    except Exception as e:
        print(f"💥 Fehler beim Check: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_vector_integrity()
