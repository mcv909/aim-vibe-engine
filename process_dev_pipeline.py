import os
import requests
import json
import time
import psycopg2
from psycopg2.extras import execute_values

# --- 🛰️ AIM MONKEY PATCH (PYTHON 3.14 & TRANSFORMERS COMPATIBILITY) ---
import sys
import logging
import transformers
from types import ModuleType

# Fix 0: Transformers-Logging-Bug unter Python 3.14 stummschalten
transformers.logging.set_verbosity_error()
logging.getLogger("transformers.modeling_attn_mask_utils").setLevel(logging.ERROR)

# Fix 1: Das rope_theta Attribut für die Config retten
if hasattr(transformers, "Qwen2Config"):
    transformers.Qwen2Config.rope_theta = 1000000.0

# Fix 2: Das verschobene Tokenizer-Modul virtuell im Speicher nachbauen
if "transformers.models.qwen2.tokenization_qwen2_fast" not in sys.modules:
    mock_qwen2_fast = ModuleType("transformers.models.qwen2.tokenization_qwen2_fast")
    if hasattr(transformers, "Qwen2TokenizerFast"):
        mock_qwen2_fast.Qwen2TokenizerFast = transformers.Qwen2TokenizerFast
        sys.modules["transformers.models.qwen2.tokenization_qwen2_fast"] = mock_qwen2_fast

# Fix 3: Das in neueren Versionen umgebaute Cache-API-System komplett faken
try:
    from transformers.cache_utils import DynamicCache
    
    if not hasattr(DynamicCache, "from_legacy_cache"):
        @classmethod
        def _from_legacy_cache(cls, past_key_values=None):
            cache = cls()
            if past_key_values is not None:
                for layer_idx in range(len(past_key_values)):
                    key_states, value_states = past_key_values[layer_idx]
                    cache.update(key_states, value_states, layer_idx)
            return cache
        DynamicCache.from_legacy_cache = _from_legacy_cache

    if not hasattr(DynamicCache, "get_usable_length"):
        def _get_usable_length(self, new_seq_length, layer_idx=0):
            if hasattr(self, "get_seq_length"):
                return self.get_seq_length(layer_idx)
            return getattr(self, "_seen_tokens", 0)
        DynamicCache.get_usable_length = _get_usable_length
        
    if not hasattr(DynamicCache, "to_legacy_cache"):
        def _to_legacy_cache(self):
            if hasattr(self, "key_cache") and hasattr(self, "value_cache"):
                return tuple(
                    (self.key_cache[i], self.value_cache[i]) 
                    for i in range(len(self.key_cache))
                )
            return ()
        DynamicCache.to_legacy_cache = _to_legacy_cache

except ImportError:
    pass
# ----------------------------------------------------------------------

from sentence_transformers import SentenceTransformer

# --- 🛰️ CONFIGURATION ---
DB_SETTINGS = {
    "dbname": "aim_db_dev",
    "user": "postgres",
    "password": "UfDAZ8uHs9RkUceKV4P1", 
    "host": "127.0.0.1",
    "port": "5432"
}

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1"
ENCODER_MODEL = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"

# --- 🛰️ SYSTEM PROMPT (SEMANTIC NORMALIZATION) ---
SYSTEM_PROMPT = (
    "Du bist ein analytischer Profiler für ein Matchmaking-System. "
    "Deine Aufgabe ist es, das persönliche Manifest des Nutzers in ein dichtes, "
    "rein faktisches und neutrales Psychogramm in der dritten Person ('Die Person...') umzuschreiben.\n\n"
    "REGELN:\n"
    "1. Zerstöre jegliche Poesie, Füllwörter, Emotionen und den individuellen Schreibstil. Homogenisiere den Text.\n"
    "2. Behalte JEDE spezifische Entität (Orte, Hardware, Hobbys, Musikgenres, Berufe, politische Ansichten) EXAKT bei.\n"
    "3. Erfinde absolut nichts hinzu! Wenn ein Thema (z.B. Politik) im Original fehlt, erwähne es nicht.\n"
    "4. Schreibe einen kompakten Fließtext. Nutze keine Listen, keine JSON-Struktur, keine Einleitung."
)

print(f"📡 Initialisiere Qwen-Encoder ({ENCODER_MODEL})...")
encoder = SentenceTransformer(ENCODER_MODEL, trust_remote_code=True)

# ❌ FIX 1: Die call_ollama Funktion mit Notbremse
def call_ollama(text):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Hier ist das Manifest:\n\n{text}"}
        ],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 800 # 🛑 LLAMA-LEINE: Zwingt Llama nach max. 800 Tokens physisch aufzuhören. Keine Endlos-Loops mehr!
        } 
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload)
        return res.json()['message']['content'].strip()
    except Exception as e:
        print(f"❌ Ollama-Fehler: {e}")
        return None

# --- ⚡ PIPELINE EXECUTION ---
def main():
    import gc
    import torch
    
    # 1. READ-PHASE: RESUME-MODUS! (Nur fehlende Profile)
    profiles = []
    conn = None
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        cur = conn.cursor()
        print("🔍 Lese fehlende Rohtexte aus der Datenbank...")
        # 🛑 RESUME-FIX: Wir laden NUR Profile, bei denen das Embedding noch fehlt!
        cur.execute("""
            SELECT profile_id, manifesto_user 
            FROM manifesto_vectors 
            WHERE manifesto_user IS NOT NULL 
              AND trim(manifesto_user) != ''
              AND embedding IS NULL; 
        """)
        profiles = cur.fetchall()
    except Exception as e:
        print(f"❌ DB Lesefehler: {e}")
        return
    finally:
        if conn:
            cur.close()
            conn.close()
            
    print(f"🟩 {len(profiles)} verbleibende Profile im Speicher. Starte Verarbeitung...")

    # 2. KI-PHASE: Llama & Qwen
    for idx, (profile_id, manifest_text) in enumerate(profiles, 1):
        print(f" [{idx}/{len(profiles)}] Verarbeite Profile-ID: {profile_id}...")
        start_p = time.time()
        
        # Stufe 1: Destillation via Llama 3.1
        distilled_text = call_ollama(manifest_text)
        if not distilled_text:
            print(f"⚠️ Überspringe Profil {profile_id} wegen Ollama-Fehler.")
            continue
            
        # 🛑 GPU-SCHUTZWALL: Qwen darf niemals mit Monster-Texten gefüttert werden!
        if len(distilled_text) > 4000:
            print(f"   ⚠️ Llama-Loop erkannt! Kappe den Müll-Text von {len(distilled_text)} auf 4000 Zeichen.")
            distilled_text = distilled_text[:4000]
            
        # Stufe 2/3: Vektorisierung
        vec_werte = encoder.encode(f"Instruct: Focus strictly on political views, core values, and ethics.\nQuery: {distilled_text}").tolist()
        vec_vibe = encoder.encode(f"Instruct: Focus strictly on music, culture, and lifestyle.\nQuery: {distilled_text}").tolist()
        vec_offenheit = encoder.encode(f"Instruct: Focus strictly on hobbies, leisure, and geographical locations.\nQuery: {distilled_text}").tolist()
        vec_komm = encoder.encode(f"Instruct: Focus strictly on technology, hardware, IT, and communication.\nQuery: {distilled_text}").tolist()
        vec_general = encoder.encode(distilled_text).tolist()
        
        # 3. WRITE-PHASE: Kurz aufmachen, feuern, zumachen
        conn_update = None
        try:
            conn_update = psycopg2.connect(**DB_SETTINGS)
            cur_update = conn_update.cursor()
            update_query = """
                UPDATE manifesto_vectors 
                SET manifesto_enc = %s, emb_werte = %s, emb_vibe = %s, 
                    emb_offenheit = %s, emb_komm = %s, embedding = %s
                WHERE profile_id = %s;
            """
            cur_update.execute(update_query, (distilled_text, vec_werte, vec_vibe, vec_offenheit, vec_komm, vec_general, profile_id))
            conn_update.commit()
        except Exception as e:
            print(f"❌ DB Schreibfehler bei Profil {profile_id}: {e}")
        finally:
            if conn_update:
                cur_update.close()
                conn_update.close()
        
        print(f" 🟩 Erfasst und geupdated in {time.time() - start_p:.2f}s.")
        
        # 🧹 RAM/VRAM MÜLLABFUHR: Befreit den Arbeitsspeicher deines MacBooks!
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        
        # ❄️ COOLING-PAUSE: 10 Minuten Tiefschlaf für das Aluminium
        time.sleep(600)

    print("\n===========================================================================")
    print("🛰️  INBOUND-PIPELINE ERFOLGREICH ABGESCHLOSSEN!")
    print("===========================================================================")

if __name__ == "__main__":
    main()