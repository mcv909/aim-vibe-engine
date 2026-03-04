import db_handler
try:
    conn = db_handler.get_connection()
    print("✅ VERBINDUNG STEHT: MacAir <-> Hetzner DB ist offen.")
    conn.close()
except Exception as e:
    print(f"❌ LEITUNG UNTERBROCHEN: {e}")
