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

def process_vibes():
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=db_handler.psycopg2.extras.DictCursor)
    
    # 1. To-Do Liste: RSA-Blobs ohne Vektor [cite: 2026-03-04]
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

    for job in jobs:
        p_id = job['profile_id']
        try:
            # 1. RSA-Entschlüsselung [cite: 2026-03-04]
            cleartext = security.decrypt_for_worker(job['manifesto_enc'], private_key_pem)
            
            # 2. Scharfe AIM-Instruktion [cite: 2025-12-30]
            instruction = (
                "Instruct: Identify user profiles that exhibit high personal resonance and shared philosophical worldviews. "
                "Focus on finding people who belong together based on their core values and lifestyle, "
                "while distinguishing clearly between opposing ideological poles.\nQuery: "
            )
            input_text = instruction + cleartext

            # 3. Vektorisierung (1536 Dimensionen) [cite: 2026-02-07]
            vector = model.encode(input_text).tolist()
            
            # 4. Vollzugsmeldung an die Matrix [cite: 2026-03-12]
            cur.execute("UPDATE manifesto_vectors SET embedding = %s WHERE profile_id = %s;", (vector, p_id))
            
            # WICHTIG: Hier setzen wir den Mail-Trigger auf FALSE (muss noch gesendet werden)
            cur.execute("""
                UPDATE profiles 
                SET is_active = true, 
                    activation_mail_sent = false 
                WHERE id = %s;
            """, (p_id,))
            
            conn.commit()
            print(f"✅ Profil {str(p_id)[:8]}... erfolgreich aktiviert.")
            
        except Exception as e:
            print(f"❌ Fehler bei Profil {p_id}: {e}")
            conn.rollback()
            
    cur.close(); conn.close()
    return True

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