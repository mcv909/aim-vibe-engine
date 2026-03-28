import db_handler
conn = db_handler.get_connection()
cur = conn.cursor()
# Wir nutzen CASCADE, um alle Abhängigkeiten (Vectors/Matches) mitzureißen
cur.execute("DROP TABLE IF EXISTS matches CASCADE;")
cur.execute("DROP TABLE IF EXISTS manifesto_vectors CASCADE;")
cur.execute("DROP TABLE IF EXISTS profiles CASCADE;")
conn.commit()
cur.close()
conn.close()
print("✅ Matrix-Speicher gelöscht. Beim nächsten App-Start wird alles frisch initialisiert.")