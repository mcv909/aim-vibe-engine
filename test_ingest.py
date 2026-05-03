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

def get_coords_safe(city_name):
    """Versucht Geocoding mit aggressivem Retry bei 429 Fehlern."""
    attempts = 0
    while attempts < 10:
        coords = logic.geocode_city(city_name)
        if coords: # Erfolg!
            return coords
        
        # Wenn wir hier landen, gab es wahrscheinlich einen 429
        attempts += 1
        wait_time = 5 * attempts # Wartet 5, 10, 15... Sekunden
        print(f"⚠️ Geocoding blockiert (429). Warte {wait_time}s... (Versuch {attempts}/10)")
        time.sleep(wait_time)
    
    return None # Nach 10 Versuchen geben wir auf

def run_import(target_file):
    if not os.path.exists(target_file):
        print(f"❌ FEHLER: Datei '{target_file}' nicht gefunden!")
        return

    df = pd.read_excel(target_file)
    print(f"📡 Starte Ingest von {len(df)} Profilen aus {target_file}...")

    for i, row in df.iterrows():
        try:
            base_email = str(row['Mailadresse']).strip()
            test_name = str(row['Name']).replace(" ", "")
            email = base_email.replace("@", f"+{test_name}@")
            
            print(f"🧬 Verarbeite: {email} ({row['Wohnort']})...")
            
            # 🛰️ DIE BRECHSTANGE: Sicherer Standort-Abruf
            coords = get_coords_safe(str(row['Wohnort']))
            if not coords:
                print(f"⚠️ Geocoding fehlgeschlagen für {row['Wohnort']}. Nutze Hamburg-Default für Test.")
                coords = (53.5511, 9.9937) # Fallback statt 'continue'

            v_key = str(row['Passwort'])
            manifesto = str(row['Manifest'])
            
            # Alters- und Größenbereiche splitten
            age_min, age_max = map(int, str(row['Sucht Alter']).replace(" ", "").split("-"))
            h_min, h_max = map(int, str(row['Sucht Größe']).replace(" ", "").split("-"))

            user_data = {
                'email': email,
                'is_email_verified': True,
                'is_active': True,
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
                'is_active': True, # Direkt auf True, damit der Worker sie sofort matcht
                'match_status': 'searching' # Direkt auf Suche
            }

            db_handler.save_profile_atomic(user_data, manifesto, PUB_KEY, v_key)
            print(f"✅ Profil {email} gesichert/aktualisiert.")
            time.sleep(1.2)

        except Exception as e:
            print(f"❌ FEHLER bei {row.get('Name')}: {e}")

if __name__ == "__main__":
    # Ermöglicht: python3 test_ingest.py delta.xlsx
    file_to_load = sys.argv[1] if len(sys.argv) > 1 else FILE_PATH
    run_import(file_to_load)