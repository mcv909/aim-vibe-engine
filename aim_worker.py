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

def run_worker():
    # 1. Status direkt abrufen (ohne Unter-Funktion)
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM embedding_queue GROUP BY status;")
    stats = dict(cur.fetchall())
    cur.execute("SELECT COUNT(*) FROM profiles WHERE is_vectorized = true;")
    vibes = cur.fetchone()[0]
    cur.close()
    conn.close()

    # 2. Die Statistik ausgeben
    print(f"\n--- 🛰️ Matrix-Status Report ---")
    print(f"⏳ Pending: {stats.get('pending', 0)} | ⚠️ Error: {stats.get('error', 0)} | 💀 Fatal: {stats.get('fatal', 0)}")
    print(f"✨ Vibes im Raum: {vibes}")
    print(f"-------------------------------\n")
    
    print(f"AIM Worker aktiv ({device}). Warte auf Matrix-Vibes...")

    while True:
        # Latest-Only Logik: Wir berechnen nur den aktuellsten Stand
        jobs = db_handler.fetch_pending_jobs_latest_only()
        
        if jobs:
            for job in jobs:
                try:
                    # 1. Entschlüsseln
                    cleartext = security.decrypt_for_worker(job['encrypted_manifesto'], private_key_pem)
                    
                    # 2. # Die neue, schärfere AIM-Instruktion
                    instruction = (
                        "Instruct: Identify user profiles that exhibit high personal resonance and shared philosophical worldviews. "
                        "Focus on finding people who belong together based on their core values and lifestyle, "
                        "while distinguishing clearly between opposing ideological poles.\nQuery: "
                    )
                    input_text = instruction + cleartext

                    # 3. Vektorisieren mit MPS-Power [cite: 2025-12-20]
                    vector = model.encode(input_text).tolist()
                    
                    # 4. In die DB schreiben & Finalisieren [cite: 2026-03-04]
                    if db_handler.finalize_vibe_vector(job['profile_id'], job['id'], vector):
                        print(f"✅ Profil {job['profile_id']} erfolgreich vektorisiert.")
                except Exception as e:
                    print(f"❌ Fehler bei Job {job['id']}: {e}")
                    db_handler.mark_job_failed(job['id'])
                    print(f"❌ Fehler bei Job {job['id']}: {e}")
                    db_handler.mark_job_failed(job['id'])
        
        time.sleep(10)

if __name__ == "__main__":
    run_worker()