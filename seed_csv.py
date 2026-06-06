import os
import csv
import json
import psycopg2
import security
from dotenv import load_dotenv

load_dotenv()

# --- 🛰️ SICHERHEITS-SETUP: Hart codiert auf die Test-Datenbank ---
DB_SETTINGS = {
    "dbname": "aim_db_dev",
    "user": "postgres",
    "password": "UfDAZ8uHs9RkUceKV4P1", 
    "host": "127.0.0.1",
    "port": "5432"
}

def get_coords(city):
    """Einfacher Lookup für die GPS-Daten"""
    lookup = {
        "Lützow": {"lat": 53.64, "lon": 11.18}, "Schwerin": {"lat": 53.63, "lon": 11.41},
        "Lübeck": {"lat": 53.86, "lon": 10.68}, "Rostock": {"lat": 54.08, "lon": 12.13},
        "Hamburg": {"lat": 53.55, "lon": 9.99}, "Wismar": {"lat": 53.89, "lon": 11.46},
        "Kiel": {"lat": 54.32, "lon": 10.12}, "Bremen": {"lat": 53.07, "lon": 8.80},
        "Stralsund": {"lat": 54.31, "lon": 13.08}, "Hannover": {"lat": 52.37, "lon": 9.73}
    }
    return lookup.get(city.strip(), {"lat": 50.11, "lon": 8.68})

def map_gender(g_str):
    g = str(g_str).lower().strip()
    if g == 'm': return 1
    if g == 'w': return 2
    return 3 

def parse_range(range_str):
    try:
        parts = str(range_str).split('-')
        return int(parts[0].strip()), int(parts[1].strip())
    except:
        return 18, 99

def seed_matrix():
    print("🚀 Starte kontrollierte Master-DNA Injektion aus CSV...")
    
    # 1. Public Key aus der .env holen
    pub_key = os.getenv("WORKER_PUBLIC_KEY")
    if not pub_key:
        print("❌ FEHLER: WORKER_PUBLIC_KEY fehlt in der .env!")
        return
    pub_key = pub_key.replace('\\n', '\n')

    # 2. Datenbank leeren
    conn = None
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        cur = conn.cursor()
        print("🧹 Leere aim_db_dev Datenbank restlos (TRUNCATE CASCADE)...")
        cur.execute("TRUNCATE TABLE profiles CASCADE;")
        conn.commit()
    except Exception as e:
        print(f"❌ DB Clean Fehler: {e}")
        return

    # 3. CSV robust einlesen
    try:
        with open('manifeste.csv', 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
        if not lines:
            print("❌ Die CSV-Datei ist komplett leer!")
            return
            
        # 🛡️ HEADER-HUNTER: Finde die WAHRE Kopfzeile (überspringe "Tabelle 1" etc.)
        start_idx = -1
        for i, line in enumerate(lines):
            if 'Name' in line and 'Mailadresse' in line:
                start_idx = i
                break
                
        if start_idx == -1:
            print("❌ Echte Spalten (Name, Mailadresse) nicht gefunden! Überprüfe die CSV.")
            return
            
        valid_lines = lines[start_idx:] 
        delimiter = ';' if ';' in valid_lines[0] else ','
        
        reader = csv.DictReader(valid_lines, delimiter=delimiter)
        
        reader.fieldnames = [str(field).strip() for field in reader.fieldnames if field]

        count = 0
        seen_emails = set() # 🛡️ Speicher für alle vergebenen E-Mails!

        for row in reader:
            name = row.get('Name', '').strip()
            if not name: continue 
            
            email_base = row.get('Mailadresse', '').strip()
            v_key = row.get('Passwort', '').strip()
            manifesto_text = row.get('Manifest', '').strip()

            if "@" in email_base:
                email_parts = email_base.split('@')
                unique_email = f"{email_parts[0]}+{name}@{email_parts[1]}"
            else:
                unique_email = email_base

            # 🛡️ DEDUPLIZIERUNG: Klon-Schutz!
            original_email = unique_email
            dup_counter = 2
            while unique_email in seen_emails:
                if "@" in original_email:
                    parts = original_email.split('@')
                    unique_email = f"{parts[0]}_{dup_counter}@{parts[1]}"
                else:
                    unique_email = f"{original_email}_{dup_counter}"
                dup_counter += 1
                
            seen_emails.add(unique_email)

            try: age = int(row.get('Alter', 30))
            except: age = 30
            try: height = int(row.get('Größe', 170))
            except: height = 170
            try: radius = int(row.get('Sucht umkreis', 50))
            except: radius = 50

            u_age_min, u_age_max = parse_range(row.get('Sucht Alter', '18-99'))
            u_height_min, u_height_max = parse_range(row.get('Sucht Größe', '150-200'))
            coords = get_coords(row.get('Wohnort', ''))

            cur.execute("""
                INSERT INTO profiles (
                    email, identity, search_for, age, height, coords, 
                    is_ukrainian, key_hash, messenger_contact, 
                    u_age_min, u_age_max, u_height_min, u_height_max, radius, 
                    is_email_verified, is_active, match_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, true, 'searching')
                RETURNING id;
            """, (
                unique_email, map_gender(row.get('Geschlecht', 'd')), map_gender(row.get('Sucht m/w/egal', 'd')), 
                age, height, json.dumps(coords), 
                False, security.hash_key(v_key), f"@{name}", 
                u_age_min, u_age_max, u_height_min, u_height_max, radius
            ))
            p_id = cur.fetchone()[0]

            # 🔐 VERSCHLÜSSELUNG FÜR DIE MATRIX
            user_enc = security.encrypt_data(manifesto_text, v_key)
            worker_enc = security.encrypt_for_worker(manifesto_text, pub_key)
            
            cur.execute("INSERT INTO manifesto_vectors (profile_id, manifesto_user, manifesto_enc) VALUES (%s, %s, %s)", (p_id, user_enc, worker_enc))
            
            count += 1
            print(f"✅ Profil injiziert: {name} ({unique_email})")
            
        conn.commit()
        print(f"\n🎉 MATRIX SEEDING ABGESCHLOSSEN: {count} Profile sicher in aim_db_dev gespeichert!")
    except Exception as e:
        print(f"❌ Fehler beim Einlesen oder Schreiben: {e}")
        if conn: conn.rollback()
    finally:
        if 'cur' in locals() and cur is not None: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    seed_matrix()