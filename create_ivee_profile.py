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
            "text": "Mir ist wichtig: Mein Hund Pinschi, Aufrichtigkeit, Offenheit, Ehrlichkeit Authentizität, Humor, Integrität. Ich bin: asexuell, Emotional, emphatisch, zielstrebig."
        },
        {
            "id": "B",
            "category": "Resilienz & Flexibilität",
            "weight": 0.20,
            "text": "Ich nsuche jenmanden, der eine starke Schuklter hat, wenn es nötig wird. Geschlecht ist vollkommen egal. Die MPErson soll mit beiden Beinen im Leben stehen aber auch gerne mal mit mir eine virtuelle Reise nach Azeroth oder so machen wollen. Derjenige soll genug Humor besitzen mich zum Lachen zu bringen aber auch genau wissen, wann es Zeit ist den nötigen Ernst zu zeigen."
        },
        {
            "id": "C",
            "category": "Musik-Ästhetik",
            "weight": 0.40,
            "text": "Da ich lange DJ war, spielt Musik generell für mich eine große Rolle, wobei ich auch gezielt die Stille suche. Es muss vor allem elektronische Musik sein in all ihren Facetten. Als DJ habe ich hauptsächlich Hardtechno aufgelegt. Derzeit gefällt mir am Besten Downtempo und CHillout."
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