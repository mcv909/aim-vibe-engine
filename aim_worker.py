import os
import time
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoConfig
from sentence_transformers import models # Wichtig: models importieren
from transformers import AutoModel, AutoConfig
from sentence_transformers import models, SentenceTransformer
import db_handler 
import security
import logging
import numpy as np # Wichtig für get_similarity [cite: 2026-02-07]
import psycopg2.extras
# Schaltet die internen Warnungen der Bibliotheken stumm
logging.getLogger("transformers").setLevel(logging.ERROR)

# 1. Device Check
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'

# 2. DAS MODELL DIREKT PATCHEN & LADEN
print(f"Lade und patche {model_id}...")
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0 # Der Fix für den Fehler [cite: 2026-03-03]
config.use_cache = False  # <--- DIESE ZEILE HINZUFÜGEN (Fix für DynamicCache) [cite: 2026-03-04]

# Wir laden das Modell physikalisch mit der korrekten Config
transformer_model = AutoModel.from_pretrained(
    model_id, 
    config=config, 
    trust_remote_code=True
)

# 3. IN SENTENCE-TRANSFORMER WRAPPEN
# Wir nutzen das geladene 'transformer_model' als Basis
word_embedding_model = models.Transformer(model_id)
word_embedding_model.auto_model = transformer_model # Wir schieben das gepatchte Modell einfach unter [cite: 2026-02-03]

pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model], device=device)

# Private Key für Hybrid-Entschlüsselung
with open("worker_private_key.pem", "r") as f:
    private_key_pem = f.read()

def get_similarity(v1, v2):
    """Berechnet die Cosinus-Ähnlichkeit im 1536-D Raum [cite: 2026-02-07]."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def process_vibes():
    conn = db_handler.get_connection()
    # Wir brauchen DictCursor für den Zugriff via Spaltennamen
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # 1. To-Do Liste: Profile ohne Vektor
    cur.execute("""
        SELECT profile_id, manifesto_enc 
        FROM manifesto_vectors 
        WHERE embedding IS NULL AND manifesto_enc IS NOT NULL 
        LIMIT 10;
    """)
    jobs = cur.fetchall()
    
    if not jobs:
        cur.close(); conn.close()
        return False

    print(f"🧬 Verarbeite {len(jobs)} neue DNA-Pakete...")

    # Unsere scharfe Master-Instruktion [cite: 2026-03-29]
    logic_enforcer = (
        "Instruct: MANDATORY DISCRIMINATION. Ignore all shared keywords and topics. "
        "Focus EXCLUSIVELY on the direction of sentiment and core values. "
        "If the text expresses rejection, hatred, or opposite worldviews, "
        "PUSH the vector to the absolute opposite end of the 1536-D space. Query: "
    )

    for job in jobs:
        p_id = job['profile_id']
        try:
            # 1. RSA-Entschlüsselung für den Worker [cite: 2026-03-04]
            cleartext = security.decrypt_for_worker(job['manifesto_enc'], private_key_pem)
            
            # 2. Vektorisierung mit Logic-Enforcer [cite: 2026-03-29]
            input_text = logic_enforcer + cleartext
            vector_np = model.encode(input_text)
            vector_list = vector_np.tolist()
            
            # 3. Vektor in die DB schreiben [cite: 2026-03-12]
            cur.execute("UPDATE manifesto_vectors SET embedding = %s WHERE profile_id = %s;", (vector_list, p_id))
            cur.execute("UPDATE profiles SET is_active = true WHERE id = %s;", (p_id,))
            conn.commit() # Vektor muss für den nächsten Schritt in der DB sein
            
            # --- NEU: SOFORTIGER MATCH-CHECK (Inkubator-Modus) [cite: 2026-04-04] ---
            run_matching_for_user(p_id, vector_np)
            
            print(f"✅ Profil {str(p_id)[:8]}... aktiviert und auf Resonanz geprüft.")
            
        except Exception as e:
            print(f"❌ Fehler bei Profil {p_id}: {e}")
            conn.rollback()
            
    cur.close(); conn.close()
    return True

def run_matching_for_user(new_id, new_vector):
    """Vergleicht das neue Profil mit dem Bestand (Anti-Spam-Logik) [cite: 2026-04-04]."""
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Alle anderen Vektoren holen [cite: 2026-03-12]
    cur.execute("SELECT profile_id, embedding FROM manifesto_vectors WHERE profile_id != %s AND embedding IS NOT NULL", (new_id,))
    others = cur.fetchall()
    
    for other in others:
        other_id = other['profile_id']
        other_vector = np.array(other['embedding'])
        
        # 1. Haben wir dieses Paar schon gemeldet? [cite: 2026-04-04]
        if should_notify(new_id, other_id):
            # 2. Resonanz berechnen [cite: 2026-02-07]
            score = get_similarity(new_vector, other_vector)
            
            # 3. Harte 0.85er Grenze [cite: 2026-03-29]
            if score >= 0.85:
                print(f"🔥 MATCH GEFUNDEN: {str(new_id)[:8]} <-> {str(other_id)[:8]} (Score: {score:.4f})")
                
                # In notified_matches verewigen (Dubletten-Sperre) [cite: 2026-04-04]
                mark_as_notified(new_id, other_id, score)
                
                # Hier käme der Mail-Trigger für beide User [cite: 2026-03-08]
                # mail_logic.send_match_notification(new_id, other_id, score)

    cur.close(); conn.close()

if __name__ == "__main__":
    print("\n--- 🛰️ AIM WORKER AKTIV ---")
    print("Scanne Matrix nach neuen Impulsen...")
    
    while True:
        # Wenn Arbeit erledigt wurde, sofort weitermachen, sonst 10 Sek. schlafen
        if not process_vibes():
            time.sleep(10)

# def run_worker():
#    # 1. Status direkt abrufen (ohne Unter-Funktion)
#    conn = db_handler.get_connection()
#    cur = conn.cursor()
#    cur.execute("SELECT status, COUNT(*) FROM embedding_queue GROUP BY status;")
#    stats = dict(cur.fetchall())
#    # ALT: cur.execute("SELECT COUNT(*) FROM profiles WHERE is_vectorized = true;")
#    # NEU:
#    cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE embedding IS NOT NULL;")
#    vibes = cur.fetchone()[0]
#    cur.close()
#    conn.close()
#
#    # 2. Die Statistik ausgeben
#    print(f"\n--- 🛰️ Matrix-Status Report ---")
#    print(f"⏳ Pending: {stats.get('pending', 0)} | ⚠️ Error: {stats.get('error', 0)} | 💀 Fatal: {stats.get('fatal', 0)}")
#    print(f"✨ Vibes im Raum: {vibes}")
#    print(f"-------------------------------\n")

if __name__ == "__main__":
    run_worker()