import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# --- IVEES DATEN-INPUT ---
# Hier fügst du ihre Texte ein, sobald sie dir diese gibt.
ivee_config = {
    "user": "Ivee",
    "location": "Lützow (Live-Test)",
    "pillars": [
        {
            "id": "A",
            "category": "Gerechtigkeit & Werte",
            "weight": 0.40, 
            "text": "HIER IVEES TEXT EINSETZEN"
        },
        {
            "id": "B",
            "category": "Resilienz & Flexibilität",
            "weight": 0.20,
            "text": "HIER IVEES TEXT EINSETZEN"
        },
        {
            "id": "C",
            "category": "Musik-Ästhetik",
            "weight": 0.40,
            "text": "HIER IVEES TEXT EINSETZEN"
        }
    ]
}

print(f"Erzeuge Vektoren für {ivee_config['user']}...")

for pillar in ivee_config["pillars"]:
    if "HIER" in pillar["text"]:
        print(f"⚠️ Warnung: Text für {pillar['category']} fehlt noch!")
        continue
        
    print(f"Vektorisierung läuft: {pillar['category']}...")
    response = client.embeddings.create(
        input=pillar["text"],
        model="text-embedding-3-small"
    )
    pillar["vector"] = response.data[0].embedding

# Speichern der Ivee-DNA
with open('ivee_master_profile.json', 'w', encoding='utf-8') as f:
    json.dump(ivee_config, f, ensure_ascii=False, indent=4)

print("\n--- ERFOLG ---")
print("Die Datei 'ivee_master_profile.json' wurde erstellt und ist bereit für das Matchmaking.")