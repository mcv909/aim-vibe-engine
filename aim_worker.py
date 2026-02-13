import os
import time
import torch
from sentence_transformers import SentenceTransformer
import db_handler # Stell sicher, dass die .env auf dem Mac die Server-IP als DB_HOST hat!
import security

# M4 Power aktivieren
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer('Alibaba-NLP/gte-Qwen2-1.5B-instruct', trust_remote_code=True, device=device)

# Deinen Private Key laden
with open("worker_private_key.pem", "r") as f:
    private_key_pem = f.read()

def run_worker():
    print("AIM Worker aktiv. Scanne Queue...")
    while True:
        conn = db_handler.get_connection()
        cur = conn.cursor()
        
        # 1. Aufgabe holen
        cur.execute("SELECT id, profile_id, encrypted_manifesto FROM embedding_queue WHERE status = 'pending' LIMIT 1")
        task = cur.fetchone()
        
        if task:
            t_id, p_id, enc_text = task
            try:
                # 2. Entschlüsseln & Vektorisieren
                cleartext = security.decrypt_for_worker(enc_text, private_key_pem)
                vector = model.encode(f"Retrieve semantically similar documents: {cleartext}").tolist()
                
                # 3. Zurückschreiben & Cleanup
                cur.execute("UPDATE profiles SET vibe_vector = %s, is_vectorized = TRUE WHERE id = %s", (vector, p_id))
                cur.execute("DELETE FROM embedding_queue WHERE id = %s", (t_id,))
                conn.commit()
                print(f"Erfolg: Profil {p_id} vektorsiert.")
            except Exception as e:
                print(f"Fehler bei Profil {p_id}: {e}")
                cur.execute("UPDATE embedding_queue SET status = 'error' WHERE id = %s", (t_id,))
                conn.commit()
        
        cur.close()
        conn.close()
        time.sleep(10) # 10 Sekunden Pause zwischen den Checks

if __name__ == "__main__":
    run_worker()