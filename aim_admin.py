import os
import shutil
import numpy as np
import psycopg2.extras
import argparse
from dotenv import load_dotenv
import db_handler

load_dotenv()

# --- 🛰️ AIM KONFIGURATION (SYNC MIT WORKER) ---
AIM_CONFIG = {
    "VALUE_MATCH_MIN": 0.82,
    "DISMATCH_VETO": 0.40,
    "FINAL_RESONANCE_MIN": 0.85,
    "WEIGHTS": {
        "werte": 0.40,
        "general": 0.20,
        "vibe": 0.15,
        "offenheit": 0.15,
        "komm": 0.10
    }
}

def print_header(title):
    print("\n" + "="*75)
    print(f"🛰️  {title.upper()}")
    print("="*75)

def get_score_visual(score):
    """Erzeugt eine visuelle Heatmap-Leiste mit Emojis."""
    blocks = int(score * 10)
    bar = "🟩" * blocks + "⬜" * (10 - blocks)
    if score < AIM_CONFIG["DISMATCH_VETO"]: color = "🟥"
    elif score < AIM_CONFIG["VALUE_MATCH_MIN"]: color = "🟨"
    else: color = "🟩"
    return f"{bar} ({color} {score:.4f})"

def check_db_connectivity():
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

def analyze_user_kaskade(email):
    """Deep-Dive Analyse der Kaskaden-Resonanz für ein spezifisches Profil."""
    print_header(f"Kaskaden-Analyse & Heatmap: {email}")
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # 🛰️ TYPEN-WANDLER: Konvertiert Numpy-Vektoren in Postgres-Listen
        def to_list(v): 
            return v.tolist() if hasattr(v, 'tolist') else v

        # 1. Anker-Daten holen
        cur.execute("""
            SELECT mv.*, p.email 
            FROM manifesto_vectors mv 
            JOIN profiles p ON p.id = mv.profile_id 
            WHERE p.email = %s;
        """, (email,))
        me = cur.fetchone()
        
        if not me or me['emb_werte'] is None:
            print(f"❌ Profil {email} wurde noch nicht kaskadiert oder existiert nicht."); return

        # 2. Alle potenziellen Partner berechnen
        # Wir wandeln hier JEDEN Vektor vor dem Senden in eine Liste um
        cur.execute("""
            SELECT p.email,
                   (1 - (mv.emb_werte <=> %s::vector)) as sw,
                   (1 - (mv.emb_vibe <=> %s::vector)) as sv,
                   (1 - (mv.emb_offenheit <=> %s::vector)) as so,
                   (1 - (mv.emb_komm <=> %s::vector)) as sk,
                   (1 - (mv.embedding <=> %s::vector)) as sg
            FROM manifesto_vectors mv
            JOIN profiles p ON p.id = mv.profile_id
            WHERE p.email != %s AND mv.emb_werte IS NOT NULL;
        """, (to_list(me['emb_werte']), to_list(me['emb_vibe']), 
              to_list(me['emb_offenheit']), to_list(me['emb_komm']), 
              to_list(me['embedding']), email))
        
        candidates = cur.fetchall()
        results = []
        w = AIM_CONFIG["WEIGHTS"]
        
        for c in candidates:
            # Veto-Logik
            has_veto = any(c[k] < AIM_CONFIG["DISMATCH_VETO"] for k in ['sv', 'so', 'sk'])
            
            final_score = (c['sw'] * w['werte'] + c['sg'] * w['general'] + 
                           c['sv'] * w['vibe'] + c['so'] * w['offenheit'] + c['sk'] * w['komm'])
            
            results.append({
                'email': c['email'], 'sw': c['sw'], 'sv': c['sv'], 'so': c['so'], 
                'sk': c['sk'], 'sg': c['sg'], 'final': final_score, 'veto': has_veto
            })

        results = sorted(results, key=lambda x: x['final'], reverse=True)

        for r in results[:15]: # Top 15 Partner anzeigen
            status = "🚫 VETO" if r['veto'] else ("🔥 MATCH" if r['final'] >= AIM_CONFIG["FINAL_RESONANCE_MIN"] else "☁️ DISSONANZ")
            print(f"\n📡 PARTNER: {r['email']} [{status}]")
            print(f"  ├─ GESAMT: {get_score_visual(r['final'])}")
            print(f"  ├─ WERTE:  {get_score_visual(r['sw'])}")
            print(f"  ├─ VIBE:   {get_score_visual(r['sv'])}")
            print(f"  ├─ OFFEN:  {get_score_visual(r['so'])}")
            print(f"  └─ KOMM:   {get_score_visual(r['sk'])}")
            
    except Exception as e:
        print(f"❌ Fehler bei der Analyse: {e}")
    finally:
        cur.close(); conn.close()

def run_standard_report():
    """Führt die Standard-Integritätsprüfung durch."""
    if not check_db_connectivity(): return
    
    # 1. Integritäts-Check
    print_header("Integritäts-Check")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profiles;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE emb_werte IS NOT NULL;")
    kaskade = cur.fetchone()[0]
    print(f"✅ DNA-Struktur: {total} Profile geladen.")
    print(f"✅ KASKADEN-STATUS: {kaskade} / {total} tiefenpsychologisch erfasst.")
    
    # 2. Pipeline Monitor
    print_header("DNA-Pipeline Monitor")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.email, (mv.embedding IS NOT NULL) as gen_vec, (mv.emb_werte IS NOT NULL) as kaskade_ok
        FROM profiles p LEFT JOIN manifesto_vectors mv ON p.id = mv.profile_id
        ORDER BY p.created_at DESC LIMIT 15;
    """)
    print(f"{'E-MAIL':<35} | {'GEN':<4} | {'KASK':<4}")
    print("-" * 50)
    for r in cur.fetchall():
        print(f"{r['email'][:33]:<35} | {'✅' if r['gen_vec'] else '❌':<4} | {'✅' if r['kaskade_ok'] else '❌':<4}")
    
    # 3. Spam-Schutz
    cur.execute("SELECT COUNT(*) FROM notified_matches;")
    matches = cur.fetchone()[0]
    print(f"\n🔒 Gespeicherte Resonanzen (notified_matches): {matches}")
    cur.close(); conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIM Matrix Admin Tool")
    parser.add_argument("--analyze", help="E-Mail des Profils für Deep-Dive Analyse")
    args = parser.parse_args()

    # Infrastruktur-Header
    t, u, f = shutil.disk_usage("/")
    print_header("Infrastruktur")
    print(f"💾 DISK: {u//(2**30)}GB / {t//(2**30)}GB")

    if args.analyze:
        analyze_user_kaskade(args.analyze)
    else:
        run_standard_report()
        print("\n💡 Tipp: Nutze --analyze <email> für eine Heatmap-Analyse.")