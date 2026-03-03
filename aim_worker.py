import os
import time
import torch
from sentence_transformers import SentenceTransformer
import db_handler 
import security

# M4 Power aktivieren
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer('Alibaba-NLP/gte-Qwen2-1.5B-instruct', trust_remote_code=True, device=device)

# Private Key laden
with open("worker_private_key.pem", "r") as f:
    private_key_pem = f.read()

def run_worker():
    print("AIM Worker aktiv. Scanne Matrix nach neuesten Vibes...")
    while True:
        # 1. Spezial-Fetch: Holt nur den NEUESTEN Stand pro User
        jobs = db_handler.fetch_pending_jobs_latest_only()
        
        if jobs:
            for job in jobs:
                t_id, p_id, enc_text = job['id'], job['profile_id'], job['encrypted_manifesto']
                try:
                    # 2. Entschlüsseln & Vektorisieren
                    cleartext = security.decrypt_for_worker(enc_text, private_key_pem)
                    # Wir nutzen den Instruct-Prefix für bessere Qualität
                    vector = model.encode(f"Retrieve semantically similar documents: {cleartext}").tolist()
                    
                    # 3. Zurückschreiben & Cleanup (In einer Funktion im db_handler bündeln!)
                    if db_handler.finalize_vibe_vector(p_id, t_id, vector):
                        print(f"✅ Erfolg: Profil {p_id} mit 1536-D Vektor stabilisiert.")
                    
                except Exception as e:
                    print(f"❌ Fehler bei Profil {p_id}: {e}")
                    db_handler.mark_job_failed(t_id)
        
        time.sleep(10) # 10 Sekunden Pause

if __name__ == "__main__":
    run_worker()