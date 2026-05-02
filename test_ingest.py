import pandas as pd
import os
import db_handler
import security
import logic
import time  # <--- DAS HIER HAT GEFEHLT!
from dotenv import load_dotenv
import sys

print("🚀 DEBUG: Script-Start...")

# 1. SETUP
load_dotenv()
PUB_KEY = os.getenv("WORKER_PUBLIC_KEY")
FILE_PATH = 'tabelle der testmanifeste.xlsx'

print(f"📂 DEBUG: Suche Datei: {FILE_PATH}")

if not os.path.exists(FILE_PATH):
    print(f"❌ FEHLER: Datei '{FILE_PATH}' wurde nicht gefunden!")
    sys.exit()

def map_gender(val):
    mapping = {'m': 1, 'w': 2, 'd': 3, 'egal': 3}
    return mapping.get(str(val).lower(), 3)

def run_import():
    df = pd.read_excel(FILE_PATH)
    print(f"📡 Starte Ingest von {len(df)} Profilen...")

    for i, row in df.iterrows():
        try:
            base_email = str(row['Mailadresse']).strip()
            test_name = str(row['Name']).replace(" ", "")
            
            # 🛰️ EMAIL-FIX: Machen wir die Mail für den Test eindeutig!
            # Erzeugt: marc.c.vietor+LenaK@gmail.com
            email = base_email.replace("@", f"+{test_name}@")
            
            print(f"🧬 Verarbeite: {email}...")
            
            v_key = str(row['Passwort'])
            manifesto = str(row['Manifest'])
            
            # Geocoding (hier liegt der 429er)
            coords = logic.geocode_city(str(row['Wohnort']))
            
            # 🛰️ RATE-LIMIT-FIX: Wir geben dem Geocoder Zeit zum Atmen
            time.sleep(1.1)
            
            # Alters- und Größenbereiche
            age_min, age_max = map(int, str(row['Sucht Alter']).replace(" ", "").split("-"))
            h_min, h_max = map(int, str(row['Sucht Größe']).replace(" ", "").split("-"))

            user_data = {
                'email': email,
                'identity': map_gender(row['Geschlecht']),
                'search_for': map_gender(row['Sucht m/w/egal']),
                'search_intent': 'b',
                'age': int(row['Alter']),
                'height': int(row['Größe']),
                'coords': coords,
                'u_age_min': age_min, 'u_age_max': age_max,
                'u_height_min': h_min, 'u_height_max': h_max,
                'radius': int(row['Sucht umkreis']),
                'is_ukrainian': False,
                'key_hash': security.hash_key(v_key),
                'is_email_verified': True,
                'is_active': False
            }

            v_token, status = db_handler.save_profile_atomic(user_data, manifesto, PUB_KEY, v_key)
            print(f"✅ Profil {email} gesichert.")

        except Exception as e:
            print(f"❌ FEHLER bei {row.get('Name')}: {e}")

if __name__ == "__main__":
    print("🎬 DEBUG: Rufe run_import() auf...")
    run_import()
    print("🏁 DEBUG: Script beendet.")