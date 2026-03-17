import db_handler

def check_db_status():
    conn = db_handler.get_connection()
    cur = conn.cursor()
    
    # 1. Check Profiles-Struktur & Anzahl
    cur.execute("SELECT COUNT(*) FROM profiles;")
    count = cur.fetchone()[0]
    
    # 2. Check ob die neuen Spalten existieren
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'profiles' 
        AND column_name IN ('is_ukrainian', 'search_for', 'u_height_min');
    """)
    columns = [row[0] for row in cur.fetchall()]
    
    # 3. Check Manifesto-Status
    cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE manifesto_user IS NOT NULL;")
    user_manifestos = cur.fetchone()[0]

    print(f"🛰️ Matrix-Report:")
    print(f"👥 Profile in DB: {count}")
    print(f"📑 Neue Spalten aktiv: {', '.join(columns)}")
    print(f"🔒 User-Manifestos (verschlüsselt): {user_manifestos}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_db_status()