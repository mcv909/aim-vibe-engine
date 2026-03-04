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
    print(f"AIM Worker aktiv ({device}). Warte auf Matrix-Vibes...")
    while True:
        # Latest-Only Logik: Wir berechnen nur den aktuellsten Stand
        jobs = db_handler.fetch_pending_jobs_latest_only()
        
        if jobs:
            for job in jobs:
                try:
                    # Entschlüsseln
                    cleartext = security.decrypt_for_worker(job['encrypted_manifesto'], private_key_pem)
                    
                    # Der "Kopf" für die GTE-Modelle [cite: 2026-03-03]
                    input_text = f"Retrieve semantically similar documents: {cleartext}"
                    
                    # Vektorisieren
                    vector = model.encode(input_text).tolist()
                    
                    # In die DB schreiben
                    if db_handler.finalize_vibe_vector(job['profile_id'], job['id'], vector):
                        print(f"✅ Profil {job['profile_id']} erfolgreich vektorisiert.")
                except Exception as e:
                    print(f"❌ Fehler bei Job {job['id']}: {e}")
                    db_handler.mark_job_failed(job['id'])
        
        time.sleep(10)

if __name__ == "__main__":
    run_worker()