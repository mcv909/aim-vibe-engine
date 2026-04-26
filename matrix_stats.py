import db_handler
import psycopg2.extras

def get_resonance_report():
    conn = db_handler.get_connection()
    # DictCursor für besser lesbare Ergebnisse
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        print("\n" + "="*40)
        print("🛰️  AIM MATRIX RESONANZ-REPORT")
        print("="*40)

        # 1. Profil-Statistiken
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_email_verified = true) as verified,
                COUNT(*) FILTER (WHERE is_active = true) as active
            FROM profiles;
        """)
        p_stats = cur.fetchone()
        
        # 2. Vektor-Status (1536-D Raum)
        cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE embedding IS NOT NULL;")
        vectorized_count = cur.fetchone()[0]

        # 3. Match-Statistiken
        cur.execute("""
            SELECT 
                COUNT(*) as match_count,
                AVG(resonance_score) as avg_score,
                MAX(resonance_score) as max_score
            FROM matches;
        """)
        m_stats = cur.fetchone()

        # Output der harten Fakten
        print(f"👥 Profile gesamt:      {p_stats['total']}")
        print(f"📧 E-Mail verifiziert:  {p_stats['verified']}")
        print(f"✨ Vektoren berechnet:  {vectorized_count}")
        print(f"🟢 Aktiv im Matching:   {p_stats['active']}")
        print("-" * 40)
        print(f"🧶 Matches gefunden:    {m_stats['match_count'] or 0}")
        if m_stats['match_count']:
            print(f"📈 Durchschnitts-Reso:  {m_stats['avg_score']:.4f}")
            print(f"🔥 Höchste Resonanz:    {m_stats['max_score']:.4f}")
        
        # 4. Top 5 Resonanzen (Anonymisiert)
        if m_stats['match_count']:
            print("-" * 40)
            print("🏆 TOP 5 RESONANZEN (ID-PAARE):")
            cur.execute("""
                SELECT user_a, user_b, resonance_score 
                FROM matches 
                ORDER BY resonance_score DESC 
                LIMIT 5;
            """)
            for row in cur.fetchall():
                # Wir zeigen nur die ersten 8 Zeichen der UUIDs
                u_a = str(row['user_a'])[:8]
                u_b = str(row['user_b'])[:8]
                print(f"  {u_a} ↔️ {u_b} | Score: {row['resonance_score']:.4f}")

    except Exception as e:
        print(f"❌ Fehler beim Auslesen der Matrix: {e}")
    finally:
        cur.close()
        conn.close()
        print("="*40 + "\n")

if __name__ == "__main__":
    get_resonance_report()