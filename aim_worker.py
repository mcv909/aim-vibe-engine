import os
import time
import torch
import numpy as np
import psycopg2.extras
from sentence_transformers import SentenceTransformer, models
from transformers import AutoModel, AutoConfig
import db_handler 
import security
import logging

# Setup [cite: 2025-12-20, 2026-03-04]
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'

print(f"🚀 Initialisiere {model_id} auf {device}...")
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0
config.use_cache = False 

transformer_model = AutoModel.from_pretrained(model_id, config=config, trust_remote_code=True)
word_embedding_model = models.Transformer(model_id)
word_embedding_model.auto_model = transformer_model

pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model], device=device)

with open("worker_private_key.pem", "r") as f:
    private_key_pem = f.read()

# --- HILFSFUNKTIONEN ---

def calculate_quality_factor(text):
    """Berechnet den Bonus (0.6 - 1.2) basierend auf der Wortanzahl [cite: 2026-03-29]."""
    words = len(text.split())
    # Logarithmische Skalierung für 'HD-Resonanz' [cite: 2025-12-30]
    return float(min(1.2, np.log10(words + 1) / 1.8))

def run_db_matching(user_id, vector_data, quality_score):
    """Führt den Vergleich direkt in SQL aus mit explizitem Type-Casting [cite: 2026-04-05]."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Sicherstellen, dass wir eine Liste senden [cite: 2026-04-05]
    if isinstance(vector_data, np.ndarray):
        vector_to_send = vector_data.tolist()
    else:
        vector_to_send = vector_data

    # WICHTIG: Das '::vector' hinter dem ersten %s zwingt Postgres zum richtigen Typ [cite: 2026-04-05]
    query = """
        SELECT mv.profile_id, 
               (1 - (mv.embedding <=> %s::vector)) * ((%s + mv.quality_score) / 2) as final_score
        FROM manifesto_vectors mv
        JOIN profiles p ON mv.profile_id = p.id
        WHERE mv.profile_id != %s 
          AND mv.embedding IS NOT NULL 
          AND p.is_active = true;
    """
    
    try:
        cur.execute(query, (vector_to_send, float(quality_score), user_id))
        potential_matches = cur.fetchall()
        
        for match in potential_matches:
            score = float(match['final_score'])
            other_id = match['profile_id']
            if score >= 0.85:
                a, b = sorted([str(user_id), str(other_id)])
                cur.execute("""
                    INSERT INTO notified_matches (user_a, user_b, last_score) 
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
                """, (a, b, score))
        
        # Den Zeitstempel setzen, damit wir im Admin 'Vollzug' sehen [cite: 2026-04-05]
        cur.execute("UPDATE manifesto_vectors SET last_matching_run = CURRENT_TIMESTAMP WHERE profile_id = %s;", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Fehler beim DB-Matching für {user_id}: {e}")
        conn.rollback()
    finally:
        cur.close(); conn.close()

def process_vibes():
    """Findet Pakete, die entweder Vektorisierung ODER Matching benötigen [cite: 2026-04-05]."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Wir suchen Profile, die KEINEN Vektor haben ODER noch NIE gematcht wurden
    cur.execute("""
        SELECT mv.profile_id, mv.manifesto_enc, mv.embedding, mv.quality_score 
        FROM manifesto_vectors mv
        WHERE (mv.embedding IS NULL OR mv.last_matching_run IS NULL) 
          AND mv.manifesto_enc IS NOT NULL 
        LIMIT 5;
    """)
    jobs = cur.fetchall()
    
    if not jobs:
        cur.close(); conn.close()
        return False

    logic_enforcer = (
        "Instruct: MANDATORY DISCRIMINATION. Ignore all shared keywords and topics. "
        "Focus EXCLUSIVELY on the direction of sentiment and core values. "
        "If the text expresses rejection, hatred, or opposite worldviews, "
        "PUSH the vector to the absolute opposite end of the 1536-D space. Query: "
    )

    for job in jobs:
        p_id = job['profile_id']
        try:
            # FALL A: Vektor fehlt noch [cite: 2026-02-07]
            if job['embedding'] is None:
                cleartext = security.decrypt_for_worker(job['manifesto_enc'], private_key_pem)
                q_score = float(calculate_quality_factor(cleartext))
                vector_np = model.encode(logic_enforcer + cleartext)
                vector_list = [float(x) for x in vector_np.tolist()]
                
                cur.execute("""
                    UPDATE manifesto_vectors SET embedding = %s, quality_score = %s 
                    WHERE profile_id = %s;
                """, (vector_list, q_score, p_id))
                cur.execute("UPDATE profiles SET is_active = true WHERE id = %s;", (p_id,))
                conn.commit()
            else:
                # FALL B: Vektor ist da, nur Matching fehlt [cite: 2026-04-05]
                vector_list = job['embedding']
                q_score = job['quality_score']

            # Jetzt das Matching für beide Fälle [cite: 2026-04-05]
            run_db_matching(p_id, vector_list, q_score)
            print(f"✅ Profil {str(p_id)[:8]}... Matching-Lauf beendet.")
            
        except Exception as e:
            print(f"❌ Fehler bei Profil {p_id}: {e}"); conn.rollback()
            
    cur.close(); conn.close()
    return True

if __name__ == "__main__":
    print("\n--- 🛰️ AIM WORKER AKTIV (SINGLE RUN MODE) ---")
    # Wir führen den Worker genau einmal aus und beenden dann
    found_work = process_vibes()
    if not found_work:
        print("📭 Keine neuen Pakete in der Matrix.")
    else:
        print("🏁 Durchlauf erfolgreich beendet.")