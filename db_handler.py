import json
import os

# TST nutzt seine eigene lokale JSON-Datei
DB_FILE = 'profiles_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_db(db_data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db_data, f, indent=2, ensure_ascii=False)