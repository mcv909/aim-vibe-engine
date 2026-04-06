import os
import shutil
import psycopg2.extras
from dotenv import load_dotenv
import db_handler

load_dotenv()

def print_header(title):
    print("\n" + "="*70)
    print(f"🛰️  {title.upper()}")
    print("="*70)

def check_db_connectivity():
    """Prüft, ob die Matrix-Leitung stabil ist."""
    try:
        conn = db_handler.get_connection()
        params = conn.get_dsn_parameters()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        ver = cur.fetchone()[0]
        print(f"✅ VERBINDUNG: {params['host']} auf Port {params['port']}")
        print(f"🐘 SERVER: {ver[:60]}...")
        cur.close(); conn.close()
        return True
    except Exception as e:
        print(f"❌ DB-VERBINDUNGSFEHLER: {e}")
        return False

def check_matrix_integrity():
    """Prüft die DNA-Kernfelder in der DB."""
    print_header("Integritäts-Check")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles';")
    fields = [row[0] for row in cur.fetchall()]
    
    core_dna = ['email', 'identity', 'search_for', 'age', 'height', 'last_interaction']
    missing = [f for f in core_dna if f not in fields]
    
    if not missing:
        print(f"✅ DNA-Struktur stabil ({len(fields)} Felder erkannt).")
    else:
        print(f"❌ FEHLENDE SEQUENZEN: {', '.join(missing)}")
    cur.close(); conn.close()

def get_pipeline_report():
    """Detaillierter Status inkl. Matching-Zeitstempel."""
    print_header("DNA-Pipeline Monitor")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.email, 
               (mv.embedding IS NOT NULL) as vec, 
               mv.last_matching_run as last_run
        FROM profiles p LEFT JOIN manifesto_vectors mv ON p.id = mv.profile_id
        ORDER BY p.created_at DESC;
    """)
    print(f"{'E-MAIL':<30} | {'VEKTOR':<6} | {'LETZTES MATCHING'}")
    print("-" * 70)
    for r in cur.fetchall():
        run_time = r['last_run'].strftime("%H:%M:%S") if r['last_run'] else "---"
        print(f"{r['email'][:28]:<30} | {'✅ JA' if r['vec'] else '❌ NEIN':<6} | {run_time}")
    cur.close(); conn.close()

def get_matrix_stats():
    """Harte Zahlen & Live-Monitoring."""
    print_header("Matrix Statistiken")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE is_email_verified = true) as verified,
            COUNT(*) FILTER (WHERE is_active = true) as active,
            COUNT(*) FILTER (WHERE last_interaction > CURRENT_TIMESTAMP - INTERVAL '15 minutes') as live_now
        FROM profiles;
    """)
    s = cur.fetchone()
    print(f"👥 Profile gesamt:      {s['total']}")
    print(f"📧 Verifiziert:         {s['verified']}")
    print(f"🟢 Aktiv im Matching:   {s['active']}")
    print(f"📡 Live-User:           {s['live_now']} (letzte 15 Min.)")
    cur.close(); conn.close()

def get_detailed_dna_report():
    """Analyse der Vektoren & Verschlüsselung."""
    print_header("Detaillierter DNA-Status")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.email, LENGTH(mv.manifesto_user) as aes, LENGTH(mv.manifesto_enc) as rsa, 
               mv.quality_score as q, (mv.embedding IS NOT NULL) as vec
        FROM profiles p JOIN manifesto_vectors mv ON p.id = mv.profile_id
        ORDER BY p.created_at DESC;
    """)
    print(f"{'E-MAIL':<30} | {'AES':<6} | {'Q-SCORE':<8} | {'VEKTOR'}")
    print("-" * 70)
    for r in cur.fetchall():
        q_val = f"{r['q']:.2f}" if r['q'] else "1.00"
        print(f"{r['email'][:28]:<30} | {r['aes']:<6} | {q_val:<8} | {'✅ JA' if r['vec'] else '❌ NEIN'}")
    cur.close(); conn.close()

def get_spam_protection_stats():
    """Status des Match-Gedächtnisses."""
    print_header("Spam-Schutz (Match-Gedächtnis)")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notified_matches;")
    count = cur.fetchone()[0]
    print(f"🔒 Gespeicherte Resonanzen (notified_matches): {count}")
    cur.close(); conn.close()

if __name__ == "__main__":
    total, used, free = shutil.disk_usage("/")
    print_header("Infrastruktur")
    print(f"💾 DISK: {used//(2**30)}GB / {total//(2**30)}GB")

    get_kaskade_analysis('marc.c.vietor@gmail.com')
    
    if check_db_connectivity():
        check_matrix_integrity()
        get_pipeline_report()
        get_matrix_stats()
        get_detailed_dna_report()
        get_spam_protection_stats()

def get_resonance_analysis(email):
    """Analysiert, warum es (kein) Match gab."""
    print_header(f"Resonanz-Analyse für {email}")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # 1. Dein Profil-Vektor und Q-Score holen
    cur.execute("SELECT profile_id, embedding, quality_score FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id WHERE p.email = %s;", (email,))
    me = cur.fetchone()
    
    if not me or me['embedding'] is None:
        print("❌ Profil noch nicht vektorisiert."); return

    # 2. Top 3 potenzielle Partner direkt in SQL berechnen
    cur.execute("""
        SELECT p.email, 
               (1 - (mv.embedding <=> %s)) * ((%s + mv.quality_score) / 2) as score
        FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id
        WHERE p.email != %s AND mv.embedding IS NOT NULL
        ORDER BY score DESC LIMIT 3;
    """, (me['embedding'], float(me['quality_score']), email))
    
    rows = cur.fetchall()
    print(f"{'PARTNER-EMAIL':<30} | {'RESONANZ-SCORE'}")
    print("-" * 50)
    for r in rows:
        print(f"{r['email'][:28]:<30} | {r['score']:.4f}")
    
    cur.close(); conn.close()

def get_resonance_analysis(email):
    """Zeigt, wie nah (oder fern) potenzielle Matches liegen."""
    print_header(f"Resonanz-Analyse: {email}")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
        SELECT mv.embedding, mv.quality_score FROM manifesto_vectors mv 
        JOIN profiles p ON p.id = mv.profile_id WHERE p.email = %s;
    """, (email,))
    me = cur.fetchone()
    
    if not me or me['embedding'] is None:
        print("❌ Profil noch nicht vektorisiert."); return

    cur.execute("""
        SELECT p.email, 
               (1 - (mv.embedding <=> %s)) * ((%s + mv.quality_score) / 2) as resonance
        FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id
        WHERE p.email != %s AND mv.embedding IS NOT NULL
        ORDER BY resonance DESC LIMIT 3;
    """, (me['embedding'], float(me['quality_score']), email))
    
    print(f"{'PARTNER':<30} | {'SCORE'}")
    print("-" * 45)
    for r in cur.fetchall():
        print(f"{r['email'][:28]:<30} | {r['resonance']:.4f}")
    cur.close(); conn.close()

def get_kaskade_analysis(email):
    """Detaillierte Einsicht in die 5 Layer-Scores."""
    print_header(f"Kaskaden-Analyse: {email}")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
        SELECT mv.profile_id, mv.emb_werte, mv.emb_vibe, mv.emb_offenheit, mv.emb_komm, mv.embedding, mv.quality_score 
        FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id WHERE p.email = %s;
    """, (email,))
    me = cur.fetchone()
    
    if not me or me['emb_werte'] is None:
        print("❌ Profil noch nicht vollständig kaskadiert."); return

    cur.execute("""
        SELECT p.email, 
               (1 - (mv.emb_werte <=> %s::vector)) as sw,
               (1 - (mv.emb_vibe <=> %s::vector)) as sv,
               (1 - (mv.emb_offenheit <=> %s::vector)) as so,
               (1 - (mv.emb_komm <=> %s::vector)) as sk,
               (1 - (mv.embedding <=> %s::vector)) as sg
        FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id
        WHERE p.email != %s AND mv.emb_werte IS NOT NULL
        ORDER BY sw DESC LIMIT 3;
    """, (me['emb_werte'], me['emb_vibe'], me['emb_offenheit'], me['emb_komm'], me['embedding'], email))
    
    print(f"{'PARTNER':<25} | {'WERT':<5} | {'VIBE':<5} | {'OFF':<5} | {'KOM':<5} | {'GEN'}")
    print("-" * 70)
    for r in cur.fetchall():
        print(f"{r['email'][:23]:<25} | {r['sw']:.2f} | {r['sv']:.2f} | {r['so']:.2f} | {r['sk']:.2f} | {r['sg']:.2f}")
    cur.close(); conn.close()

# Im __main__ Teil hinzufügen:
# get_kaskade_analysis('marc.c.vietor@gmail.com')
    
    print("\n✅ Admin-Check beendet.")