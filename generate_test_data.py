import json
import os
import random
from openai import OpenAI
from dotenv import load_dotenv

# --- INITIALISIERUNG ---
load_dotenv()
client = OpenAI()

# --- KONFIGURATION FÜR v0.2.1 ---
CITIES = ["Lützow", "Obertshausen", "Frankfurt", "Hamburg", "Berlin", "München", "Köln"]
GENDERS = ["m", "w", "d"]
SEARCH_OPTIONS = ["Partnerin (w)", "Partner (m)", "Freunde (egal)"]

def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def run_upgrade():
    archetypes = [
        {"name": "R. Giskard", "bio": "Gerechtigkeit ist ein kosmisches Gesetz."},
        {"name": "R. Daneel", "bio": "Harmonie durch Verbindung und Geschichte."},
        {"name": "R. Sammy", "bio": "Harter Industrial Techno. Präzision pur."},
        {"name": "R. Jander", "bio": "Klangfarben und emotionale Tiefe."},
        {"name": "R. Fastolfe", "bio": "Wissenschaftliche Distanz und Resilienz."},
        {"name": "R. Gladia", "bio": "Freiheit und Mut zum Abgrund."},
        {"name": "R. Dors", "bio": "Schutz der Schwachen durch Struktur."},
        {"name": "R. Eto", "bio": "Flexibilität als höchste Form der Macht."},
        {"name": "R. Baley", "bio": "Wahrheit auf dem nassen Asphalt der Stadt."},
        {"name": "R. Seldon", "bio": "Statistische Perfektion im Miteinander."}
    ]

    profiles_db = []
    print("🚀 [UPGRADE] AIM aktualisiert die 100 Seelen für v0.2.1...")

    for i in range(100):
        base = archetypes[i % len(archetypes)]
        name = f"{base['name']} #{i+1}" if i >= 10 else base['name']
        
        # NEU: Zufällige Metadaten für die Filterlogik
        gender = random.choice(GENDERS)
        loc = random.choice(CITIES)
        search = random.choice(SEARCH_OPTIONS)

        print(f"➡️  Vektorisierung & Metadaten: {name} ({gender} in {loc})", end="\r")
        
        vector = get_embedding(base['bio'])
        
        profiles_db.append({
            "id": f"bot_{i}",
            "name": name,
            "gender": gender,
            "search": search,
            "loc": loc,
            "type": "test_R",
            "manifesto": base['bio'],
            "vector": vector,
            "timestamp": "2025-12-26T21:00:00"
        })

    with open('profiles_db.json', 'w', encoding='utf-8') as f:
        json.dump(profiles_db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ [DONE] 100 Profile für v0.2.1 in 'profiles_db.json' aktualisiert!")

if __name__ == "__main__":
    run_upgrade()