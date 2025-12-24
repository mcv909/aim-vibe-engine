import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Umgebung laden
load_dotenv()
client = OpenAI()

# 2. Dein Datensatz
profile_data = {
    "user": "Marc",
    "statement": "Musik ist für mich kein Konsumgut, sondern ein essentielles Ordnungssystem (Fokus auf Techno/Klangästhetik).",
    "metadata": {
        "category": "music_values",
        "date": "2025-12-24"
    }
}

print(f"Verarbeite Statement für: {profile_data['user']}...")

# 3. Vektor erzeugen
response = client.embeddings.create(
    input=profile_data["statement"],
    model="text-embedding-3-small"
)

# 4. Daten zusammenführen
profile_data["vector"] = response.data[0].embedding

# 5. Als JSON-Datei speichern
with open('marc_profile.json', 'w', encoding='utf-8') as f:
    json.dump(profile_data, f, ensure_ascii=False, indent=4)

print("\n--- ERFOLG ---")
print("Datei 'marc_profile.json' wurde erstellt.")
print("Dieser Datensatz ist bereit für den Abgleich (Matchmaking).")