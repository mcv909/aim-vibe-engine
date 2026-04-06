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

# --- 🛰️ AIM KONFIGURATION (THRESHOLD-ZENTRALE) --- [cite: 2026-04-06]
AIM_CONFIG = {
    "VALUE_MATCH_MIN": 0.82,       # Harte Hürde für Grundwerte
    "DISMATCH_VETO": 0.40,        # Ab hier gilt ein Layer als Ausschlusskriterium
    "FINAL_RESONANCE_MIN": 0.85,   # Benachrichtigung erst ab diesem Gesamtwert
    "WEIGHTS": {                   # Gewichtung der Layer für den Final-Score
        "werte": 0.40,
        "general": 0.20,
        "vibe": 0.15,
        "offenheit": 0.15,
        "komm": 0.10
    }
}

CATEGORY_PROMPTS = {
    "werte": "Instruct: FOCUS ON MORAL COMPASS. Extract values regarding social justice, universalism, and benevolence. Query: ",
    "vibe": "Instruct: FOCUS ON SOCIAL BATTERY. Analyze the need for stimulation vs. solitude. Focus on the 'how' of social interaction. Query: ",
    "offenheit": "Instruct: FOCUS ON INTELLECTUAL OPENNESS. Analyze the attitude towards new experiences, arts, and unconventional lifestyles. Query: ",
    "komm": "Instruct: FOCUS ON LINGUISTIC NUANCE. Identify the use of irony, sarcasm, and directness. Query: "
}

# --- REPARIERTES MODELL-SETUP --- [cite: 2026-04-06]
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'

print(f"🚀 Initialisiere {model_id} auf {device} (mit Qwen-Fix)...")
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0  # Der fehlende Wert [cite: 2026-04-06]
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
    """Berechnet den Bonus (0.6 - 1.2) [cite: 2026-03-29, 2025-12-30]."""
    words = len(text.split())
    return float(min(1.2, np.log10(words + 1) / 1.8))

def run_db_matching(user_id, vectors_dict, quality_score):
    """Kaskadierendes Matching: Erst Werte-Check, dann Veto-Filter [cite: 2026-04-06]."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Vorbereitung der Vektoren als Listen für Postgres [cite: 2026-04-05]
    v = {k: ([float(x) for x in vec.tolist()] if isinstance(vec, np.ndarray) else vec) 
         for k, vec in vectors_dict.items()}

    query = """
        SELECT mv.profile_id,
               (1 - (mv.emb_werte <=> %s::vector)) as sw,
               (1 - (mv.emb_vibe <=> %s::vector)) as sv,
               (1 - (mv.emb_offenheit <=> %s::vector)) as so,
               (1 - (mv.emb_komm <=> %s::vector)) as sk,
               (1 - (mv.embedding <=> %s::vector)) as sg
        FROM manifesto_vectors mv
        JOIN profiles p ON mv.profile_id = p.id
        WHERE mv.profile_id != %s AND mv.emb_werte IS NOT NULL AND p.is_active = true
          AND (1 - (mv.emb_werte <=> %s::vector)) >= %s;
    """
    
    try:
        cur.execute(query, (v['werte'], v['vibe'], v['offenheit'], v['komm'], v['general'], 
                            user_id, v['werte'], AIM_CONFIG["VALUE_MATCH_MIN"]))
        candidates = cur.fetchall()
        
        for cand in candidates:
            # Veto-Prüfung (Ausschluss bei krassem Gegensatz) [cite: 2026-04-06]
            if any(cand[key] < AIM_CONFIG["DISMATCH_VETO"] for key in ['sv', 'so', 'sk']):
                continue 
            
            # Gewichteter Final-Score [cite: 2026-04-06]
            w = AIM_CONFIG["WEIGHTS"]
            final_score = (cand['sw'] * w['werte'] + cand['sg'] * w['general'] + 
                           cand['sv'] * w['vibe'] + cand['so'] * w['offenheit'] + cand['sk'] * w['komm'])
            
            if final_score >= AIM_CONFIG["FINAL_RESONANCE_MIN"]:
                a, b = sorted([str(user_id), str(cand['profile_id'])])
                cur.execute("""
                    INSERT INTO notified_matches (user_a, user_b, last_score) 
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
                """, (a, b, final_score))
        
        cur.execute("UPDATE manifesto_vectors SET last_matching_run = CURRENT_TIMESTAMP WHERE profile_id = %s;", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Kaskaden-Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()

def process_vibes():
    """DNA-Sezierung in 5 Layer [cite: 2026-04-06]."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT profile_id, manifesto_enc, embedding, quality_score, emb_werte 
        FROM manifesto_vectors WHERE (embedding IS NULL OR last_matching_run IS NULL) 
        AND manifesto_enc IS NOT NULL LIMIT 5;
    """)
    jobs = cur.fetchall()
    if not jobs:
        cur.close(); conn.close(); return False

    logic_enforcer = (
        "Instruct: MANDATORY DISCRIMINATION. Ignore all shared keywords and topics. "
        "Focus EXCLUSIVELY on the direction of sentiment and core values. "
        "If the text expresses rejection, hatred, or opposite worldviews, "
        "PUSH the vector to the absolute opposite end of the 1536-D space. Query: "
    )

    for job in jobs:
        p_id = job['profile_id']
        try:
            if job['emb_werte'] is None: # Vollständige Neu-Vektorisierung [cite: 2026-04-06]
                cleartext = security.decrypt_for_worker(job['manifesto_enc'], private_key_pem)
                q_score = float(calculate_quality_factor(cleartext))
                
                vectors = {'general': model.encode(logic_enforcer + cleartext)}
                for key, prompt in CATEGORY_PROMPTS.items():
                    vectors[key] = model.encode(prompt + cleartext)
                
                v_lists = {k: [float(x) for x in vec.tolist()] for k, vec in vectors.items()}
                
                cur.execute("""
                    UPDATE manifesto_vectors SET embedding = %s, emb_werte = %s, emb_vibe = %s, 
                    emb_offenheit = %s, emb_komm = %s, quality_score = %s WHERE profile_id = %s;
                """, (v_lists['general'], v_lists['werte'], v_lists['vibe'], v_lists['offenheit'], v_lists['komm'], q_score, p_id))
                cur.execute("UPDATE profiles SET is_active = true WHERE id = %s;", (p_id,))
                conn.commit()
                current_vectors = v_lists
            else:
                current_vectors = {'general': job['embedding'], 'werte': job['emb_werte']} # (vereinfacht)

            run_db_matching(p_id, current_vectors, q_score or job['quality_score'])
            print(f"✅ Profil {str(p_id)[:8]}... Kaskaden-Matching beendet.")
        except Exception as e:
            print(f"❌ Fehler bei Profil {p_id}: {e}"); conn.rollback()
    cur.close(); conn.close(); return True

if __name__ == "__main__":
    print("\n--- 🛰️ AIM WORKER AKTIV (KASKADEN-MODUS) ---")
    while True:
        if not process_vibes():
            time.sleep(10)