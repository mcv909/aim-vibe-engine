import db_handler

def rebuild():
    print("🛠️ Starte Force-Rebuild der Matrix...")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    try:
        # 1. Tabellen radikal löschen
        cur.execute("DROP TABLE IF EXISTS matches CASCADE;")
        cur.execute("DROP TABLE IF EXISTS manifesto_vectors CASCADE;")
        cur.execute("DROP TABLE IF EXISTS profiles CASCADE;")
        print("✅ Alte Tabellen gelöscht.")

        # 2. Profiles neu anlegen
        cur.execute("""
            CREATE TABLE profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                identity INT, search_for INT, age INT, height INT, 
                coords JSONB, u_age_min INTEGER, u_age_max INTEGER,
                u_height_min INTEGER, u_height_max INTEGER, radius INTEGER,
                is_ukrainian BOOLEAN DEFAULT FALSE, is_email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT FALSE, key_hash TEXT, messenger_contact TEXT,
                verification_token UUID DEFAULT gen_random_uuid(),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. Manifesto Vectors mit der manifesto_user Spalte! [cite: 2026-03-15]
        cur.execute("""
            CREATE TABLE manifesto_vectors (
                profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
                manifesto_user TEXT,
                manifesto_enc TEXT,
                embedding vector(1536)
            );
        """)
        
        conn.commit()
        print("✨ Fundament erfolgreich neu gegossen (inkl. manifesto_user).")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        conn.rollback()
    finally:
        cur.close(); conn.close()

if __name__ == "__main__":
    rebuild()