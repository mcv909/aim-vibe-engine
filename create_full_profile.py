import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

profile_config = {
    "user": "Marc Vietor",
    "location": "Lützow (Holiday-Hack Edition)",
    "pillars": [
        {
            "id": "A",
            "category": "Gerechtigkeit & Werte",
            "weight": 0.40,
            "text": "Wahrer Erfolg bemisst sich für mich nicht am Kontostand, sondern an der Integrität und dem Beitrag zu einer gerechteren Gesellschaft."
        },
        {
            "id": "B",
            "category": "Resilienz & Flexibilität",
            "weight": 0.20,
            "text": "Ich suche jemanden, der das Leben nicht als starre Liste begreift, sondern die Flexibilität besitzt, auch in stürmischen Zeiten den Humor und die Haltung zu bewahren."
        },
        {
            "id": "C",
            "category": "Musik-Ästhetik",
            "weight": 0.40,
            "text": "Musik ist für mich kein Konsumgut, sondern ein essentielles Ordnungssystem (Fokus auf Techno/Klangästhetik)."
        },
        {
            "id": "D",
            "category": "Adams-Singularität",
            "weight": 0.00,
            "text": "Die Codierung dieser Werte an Heiligabend war rein statistischer Zufall, da die KI eh nicht gläubig ist und der Proband ein Hardcore-Atheist – aber es macht immensen Spaß!"
        }
    ]
}

print(f"Erzeuge Master-Vektoren für den Vietor-Vektor...")

for pillar in profile_config["pillars"]:
    print(f"Vektorisierung läuft: {pillar['category']}...")
    response = client.embeddings.create(
        input=pillar["text"],
        model="text-embedding-3-small"
    )
    pillar["vector"] = response.data[0].embedding

with open('marc_master_profile.json', 'w', encoding='utf-8') as f:
    json.dump(profile_config, f, ensure_ascii=False, indent=4)

print("\n--- DURCHSTICH ERFOLGT ---")
print("Die Datei 'marc_master_profile.json' wurde mit allen 4 Säulen in Lützow erstellt.")