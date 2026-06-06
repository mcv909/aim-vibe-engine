import os
import shutil
import numpy as np
import psycopg2.extras
import argparse
from dotenv import load_dotenv
import db_handler

load_dotenv()

def print_header(title):
    """Erzeugt die einheitlichen AIM-Terminal-Header."""
    print("\n" + "="*75)
    print(f"🛰️  {title.upper()}")
    print("="*75)

# --- 🛰️ AIM KONFIGURATION (KALIBRIERT FÜR QWEN2 INSTRUCT & LLAMA) ---
AIM_CONFIG = {
    "VALUE_MATCH_MIN": 0.35,     # 🟨 Ab 0.35 wird es solides Mittelfeld
    "DISMATCH_VETO": 0.28,       # 🟥 Unter 0.28 ist hartes Veto / Gegenpol
    "FINAL_RESONANCE_MIN": 0.48, # 🔥 Ab 0.48 ist es ein Klon / Top-Match
    "WEIGHTS": {
        "werte": 0.40,
        "general": 0.20,
        "vibe": 0.15,
        "offenheit": 0.15,
        "komm": 0.10
    }
}

# --- 🛰️ GOLD STANDARD MAPPING ---
GOLD_STANDARD = {
    "LenaK": "100%", "MarcAnkerTest": "100%", "SandraM": "100%", 
    "MiriamT": "100%", "KatjaR": "100%", "AnjaV": "100%",
    "JanaM": "100%", "MiriamP": "100%", "LauraR": "100%", "AnkeB": "100%",
    "ClaudiaH": "Werte verschieden", "PetraW": "Werte verschieden",
    "JuliaF": "Werte verschieden", "MarieS": "Werte verschieden",
    "SophiaB": "Werte verschieden", "TanjaK": "50/50", "NinaP": "50/50",
    "VeraL": "50/50", "ElenaG": "50/50", "InesB": "50/50", 
    "JuliaH": "50/50", "SteffiP": "50/50", "NinaT": "50/50",
    "EvaV": "50/50", "AnalyGerechtFanat": "Offen!", "TechnoKünstlerin": "Offen!",
    "MarcAnker": "Anker-Profil"
}

def get_expected_status(email):
    """Extrahiert den Namen aus der E-Mail und liefert den Soll-Status."""
    try:
        name = email.split('+')[1].split('@')[0]
        return GOLD_STANDARD.get(name, "Unbekannt")
    except:
        return "Basis-Profil"

def get_score_visual(score):
    """Erzeugt eine visuelle Heatmap-Leiste (Angepasst an die neue Qwen2 Physik)."""
    # 0.60 ist das absolute Qwen-Maximum für echte Texte. 
    # Wir normieren das optisch, damit der Balken wieder voll wird.
    norm_score = min(1.0, score / 0.60) 
    blocks = int(norm_score * 10)
    bar = "🟩" * blocks + "⬜" * (10 - blocks)
    
    if score < AIM_CONFIG["DISMATCH_VETO"]: color = "🟥"
    elif score < AIM_CONFIG["VALUE_MATCH_MIN"]: color = "🟨"
    else: color = "🟩"
    return f"{bar} ({color} {score:.4f})"

def analyze_user_kaskade(email):
    conn = db_handler.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        def to_list(v): return v.tolist() if hasattr(v, 'tolist') else v

        cur.execute("SELECT mv.* FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id WHERE p.email = %s;", (email,))
        me = cur.fetchone()
        
        if not me or me['emb_werte'] is None:
            print(f"❌ Profil {email} wurde noch nicht kaskadiert."); return

        cur.execute("""
            SELECT p.email,
                   (1 - (mv.emb_werte <=> %s::vector)) as sw,
                   (1 - (mv.emb_vibe <=> %s::vector)) as sv,
                   (1 - (mv.emb_offenheit <=> %s::vector)) as so,
                   (1 - (mv.emb_komm <=> %s::vector)) as sk,
                   (1 - (mv.embedding <=> %s::vector)) as sg
            FROM manifesto_vectors mv JOIN profiles p ON p.id = mv.profile_id
            WHERE p.email != %s AND mv.emb_werte IS NOT NULL;
        """, (to_list(me['emb_werte']), to_list(me['emb_vibe']), to_list(me['emb_offenheit']), to_list(me['emb_komm']), to_list(me['embedding']), email))
        
        candidates = cur.fetchall()
        results = []
        w = AIM_CONFIG["WEIGHTS"]
        
        for c in candidates:
            final_score = (c['sw'] * w['werte'] + c['sg'] * w['general'] + 
                           c['sv'] * w['vibe'] + c['so'] * w['offenheit'] + c['sk'] * w['komm'])
            results.append({
                'email': c['email'], 'sw': c['sw'], 'sv': c['sv'], 'so': c['so'], 
                'sk': c['sk'], 'sg': c['sg'], 'final': final_score
            })

        results = sorted(results, key=lambda x: x['final'], reverse=True)

        print(f"\n{'PARTNER (EMAIL)':<45} | {'SOLL':<18} | {'IST-SCORE'}")
        print("-" * 85)
        
        # ❌ Die 15er-Sperre ist hier nun endgültig raus. Wir sehen ALLE!
        for r in results:
            exp = get_expected_status(r['email'])
            ist = "🔥 MATCH" if r['final'] >= AIM_CONFIG["FINAL_RESONANCE_MIN"] else "☁️ DISSONANZ"
            print(f"{r['email'][:43]:<45} | {exp:<18} | {ist}")
            print(f"  └─ HEATMAP: {get_score_visual(r['final'])}")
            print(f"  └─ LAYERS : [Werte:{r['sw']:.4f}] [Gen:{r['sg']:.4f}] [Vibe:{r['sv']:.4f}] [Off:{r['so']:.4f}] [Komm:{r['sk']:.4f}]")
            
    finally:
        cur.close(); conn.close()

def check_db_connectivity():
    try:
        conn = db_handler.get_connection()
        conn.close()
        return True
    except:
        return False

def run_standard_report():
    if not check_db_connectivity(): return
    
    print_header("Integritäts-Check")
    conn = db_handler.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profiles;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM manifesto_vectors WHERE emb_werte IS NOT NULL;")
    kaskade = cur.fetchone()[0]
    print(f"✅ DNA-Struktur: {total} Profile geladen.")
    print(f"✅ KASKADEN-STATUS: {kaskade} / {total} tiefenpsychologisch erfasst.")
    
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
    
    cur.execute("SELECT COUNT(*) FROM notified_matches;")
    matches = cur.fetchone()[0]
    print(f"\n🔒 Gespeicherte Resonanzen (notified_matches): {matches}")
    cur.close(); conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIM Matrix Admin Tool")
    parser.add_argument("--analyze", help="E-Mail des Profils für Deep-Dive Analyse")
    args = parser.parse_args()

    t, u, f = shutil.disk_usage("/")
    print_header("Infrastruktur")
    print(f"💾 DISK: {u//(2**30)}GB / {t//(2**30)}GB")

    if args.analyze:
        analyze_user_kaskade(args.analyze)
    else:
        run_standard_report()