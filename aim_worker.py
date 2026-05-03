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

# --- 🛰️ AIM KONFIGURATION (THRESHOLD-ZENTRALE) ---
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
    "werte": "Instruct: Represent the ethical values and worldviews of this person.\nQuery: ",
    "vibe": "Instruct: Represent the social temperament and energy level of this person.\nQuery: ",
    "offenheit": "Instruct: Represent the curiosity and openness to new experiences of this person.\nQuery: ",
    "komm": "Instruct: Represent the communication style and linguistic tone of this person.\nQuery: "
}

# --- REPARIERTES MODELL-SETUP ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'

print(f"🚀 Initialisiere {model_id} auf {device} (mit Qwen-Fix)...")
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0  # Der fehlende Wert
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
    """Berechnet den Bonus (0.6 - 1.2)."""
    words = len(text.split())
    return float(min(1.2, np.log10(words + 1) / 1.8))

def run_db_matching(user_id, vectors_dict, quality_score):
    """Kaskadierendes Matching: Erst Werte-Check, dann Veto-Filter."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Vorbereitung der Vektoren als Listen für Postgres
    v = {k: ([float(x) for x in vec.tolist()] if isinstance(vec, np.ndarray) else vec) 
         for k, vec in vectors_dict.items()}

    query = """
        SELECT mv.profile_id,
               (1 - (mv.emb_werte <=> %s::vector)) as sw,
               (1 - (mv.emb_vibe <=> %s::vector)) as sv,
               (1 - (mv.emb_offenheit <=> %s::vector)) as so,
               (1 - (mv.emb_komm <=> %s::vector)) as sk,
               (1 - (mv.embedding <=> %s::vector)) as sg,
               p_target.email
        FROM manifesto_vectors mv
        JOIN profiles p_target ON mv.profile_id = p_target.id
        JOIN profiles p_me ON p_me.id = %s
        WHERE mv.profile_id != %s 
          AND p_target.is_active = true
          -- 🛰️ STATUS-FILTER: Nur wer aktiv sucht [cite: 2026-04-06]
          AND p_target.match_status = 'searching'
          AND p_me.match_status = 'searching'
          -- 🛰️ DOPPEL-MATCH-SCHUTZ: Gedächtnis der Matrix [cite: 2026-04-06]
          AND NOT EXISTS (
              SELECT 1 FROM notified_matches nm 
              WHERE (nm.user_a = LEAST(%s::uuid, mv.profile_id) 
                AND nm.user_b = GREATEST(%s::uuid, mv.profile_id))
          )
          AND (
            (p_me.search_intent IN ('p', 'b') AND p_target.search_intent IN ('p', 'b')
             AND (p_me.search_for = p_target.identity OR p_me.search_for = 3)
             AND (p_target.search_for = p_me.identity OR p_target.search_for = 3))
            OR 
            (p_me.search_intent IN ('f', 'b') AND p_target.search_intent IN ('f', 'b'))
          )
          AND (1 - (mv.emb_werte <=> %s::vector)) >= %s;
    """
    
    try:
        cur.execute(query, (v['werte'], v['vibe'], v['offenheit'], v['komm'], v['general'], 
                            user_id, user_id, str(user_id), str(user_id), v['werte'], AIM_CONFIG["VALUE_MATCH_MIN"]))
        candidates = cur.fetchall()
        
        for cand in candidates:
            # Veto-Prüfung (Ausschluss bei krassem Gegensatz)
            if any(cand[key] < AIM_CONFIG["DISMATCH_VETO"] for key in ['sv', 'so', 'sk']):
                continue 
            
            # Gewichteter Final-Score
            w = AIM_CONFIG["WEIGHTS"]
            final_score = (cand['sw'] * w['werte'] + cand['sg'] * w['general'] + 
                           cand['sv'] * w['vibe'] + cand['so'] * w['offenheit'] + cand['sk'] * w['komm'])
            
            if final_score >= AIM_CONFIG["FINAL_RESONANCE_MIN"]:
                a, b = sorted([str(user_id), str(cand['profile_id'])])
                cur.execute("""
                    INSERT INTO notified_matches (user_a, user_b, last_score) 
                    VALUES (%s::uuid, %s::uuid, %s) ON CONFLICT DO NOTHING;
                """, (a, b, final_score))
                                
                # 🛰️ AUTOMATISCHER FOKUS-MODUS
                cur.execute("""
                    UPDATE profiles SET match_status = 'focusing' 
                    WHERE id IN (%s, %s);
                """, (str(user_id), str(cand['profile_id'])))
                print(f"🎯 Resonanz gefunden! Fokus-Modus für {a[:8]} und {b[:8]} aktiviert.")
        
        cur.execute("UPDATE manifesto_vectors SET last_matching_run = CURRENT_TIMESTAMP WHERE profile_id = %s;", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Kaskaden-Fehler: {e}"); conn.rollback()
    finally:
        cur.close(); conn.close()

def process_vibes():
    """DNA-Sezierung in 5 Layer mit korrektem Logic Enforcer."""
    print("📡 Versuche Datenbank-Verbindung...", end=" ", flush=True)
    try:
        conn = db_handler.get_connection()
        print("✅")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
        
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    print("🔎 Suche DNA-Pakete...", end=" ", flush=True)
    cur.execute("""
        SELECT mv.profile_id, mv.manifesto_enc, mv.embedding, mv.quality_score, mv.emb_werte 
        FROM manifesto_vectors mv
        JOIN profiles p ON p.id = mv.profile_id
        WHERE (mv.embedding IS NULL OR mv.emb_werte IS NULL)
        AND mv.manifesto_enc IS NOT NULL
        AND p.is_active = true
        AND p.is_email_verified = true
        LIMIT 5;
    """)
    jobs = cur.fetchall()
    print(f"✅ ({len(jobs)} gefunden)")
    
    if not jobs:
        cur.close(); conn.close()
        return False

    # DER FIX: Der vollständige Logic Enforcer für den General-Vektor
    logic_enforcer = "Instruct: Represent this person's core identity for personality matching.\nQuery: "

    for job in jobs:
        p_id = job['profile_id']
        print(f"🧬 Starte 5-Layer-Analyse für {str(p_id)[:8]}...", end=" ", flush=True)
        try:
            cleartext = security.decrypt_for_worker(job['manifesto_enc'], private_key_pem)
            q_score = float(calculate_quality_factor(cleartext))
            
            # 1. General Vektor
            vectors = {'general': model.encode(logic_enforcer + cleartext)}
            
            # 2. Die 4 Kaskaden-Layer
            for key, prompt in CATEGORY_PROMPTS.items():
                vectors[key] = model.encode(prompt + cleartext)
            
            # Umwandlung für Postgres
            v_lists = {k: [float(x) for x in vec.tolist()] for k, vec in vectors.items()}
            
            cur.execute("""
                UPDATE manifesto_vectors SET 
                    embedding = %s, emb_werte = %s, emb_vibe = %s, 
                    emb_offenheit = %s, emb_komm = %s, quality_score = %s 
                WHERE profile_id = %s;
            """, (v_lists['general'], v_lists['werte'], v_lists['vibe'], 
                  v_lists['offenheit'], v_lists['komm'], q_score, p_id))
            
            cur.execute("UPDATE profiles SET is_active = true WHERE id = %s;", (p_id,))
            conn.commit()
            
            # Matching anstoßen
            run_db_matching(p_id, v_lists, q_score)
            print("✅")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")
            conn.rollback()
            
    cur.close(); conn.close()
    return True

if __name__ == "__main__":
    print("\n--- 🛰️ AIM WORKER AKTIV (KASKADEN-MODUS) ---")
    while True:
        if not process_vibes():
            time.sleep(10)