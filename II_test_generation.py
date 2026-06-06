import requests
import json
import time

# --- 🛰️ AIM OLLAMA CONFIG ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1"  # Oder "qwen2.5:7b"

# --- 🧬 DEIN KOHLENSTOFF-ORIGINAL ---
manifest_original = """Liebe Musik, die ist eigentlich ständig um mich. Ich bevorzuge hier Techno bzw. elektronische Musik. Bin aber dahingehend offen und höre auch gerne mal Rock oder Pop (Sting, Police, Led Zeppelin, NIN etc.).
Aber am liebsten eben elektronische Musik, absoluter Faible für Drum n Bass/Jungle, Minimal und eben Techno und Acid.
Es gibt kein geileres geräusch als eine geil kreischende 303 - noch ein fetter Bass dazu und ne schön dahindüdelnde Melodie > BÄM bin glücklich :)
Drehe gerne mal etwas an Potis herum, mache, für mich, auch gerne mal, mit der entsprechende Muse, elektronische Musik.
Genieße aber auch gerne mal die Einsamkeit und die Ruhe im Wald und, vor allem, am Meer. Deswegen verschlug es mich auch nach, erst Rostock, dann jetzt Lützow.
Pendle zwischen Ffm Bankstadt wo ich arbeite (wenn ich vor Ort sein muss) oder eben Lützow in der selbst ausgesuchten Homebase.
Der switch zwischen Großstadt und kleinem Ort ist toll, immer etwas anderes und spannend. Bin auch gerne mal in Hamburg (tolle Stadt).
Ansonsten, wenn es die Zeit zulässst (Arbeite in der IT) fotografiere ich gerne (People und Street).
Ich bin eher links eingestellt, Politik ist wichtig wenn auch nicht immer das besteテーマ - muss man Bock drauf haben.
Trinke so gut wie keinen Alkohol aber rauchen ist leider ein aktuell noch bestehendes Laster (keine Kippen, Iqos, aber ist auch nicht viel besser, stinkt wenigstens nicht so).
Spazieren gehen, Biken, am Strand sitzen und sinnfrei aufs Meer starren, das finde ich großartig. Nachts durch eine Stadt wandern, auch toll."""

# Der System-Prompt diktiert das exakte JSON-Format
system_prompt = (
    "Du bist ein hochpräziser semantischer Profiler für ein Matchmaking-System.\n"
    "Deine Aufgabe ist es, das Freitext-Manifest eines Nutzers in ein strukturiertes, "
    "nuanciertes JSON-Datenblatt zu übersetzen. Das Ziel ist es, das sprachliche Rauschen "
    "zu entfernen, aber alle essentiellen Identitätsmarker vollständig zu erhalten.\n\n"
    
    "STRIKTE ARCHITEKTUR-REGELN:\n"
    "1. Keine Erfindungen: Nutze ausschließlich Fakten und Konzepte, die direkt und explizit aus dem bereitgestellten Textgraphen hervorgehen.\n"
    "2. Technische Spezifität: Behalte exakte Zahlenbezeichnungen, Modellnummern, spezifische Gerätenamen oder technische Kürzel zwingend bei. Sie dürfen niemals als bloße Prosa ignoriert werden.\n"
    "3. Verneinungen erfassen: Wenn ein Nutzer explizit erwähnt, etwas NICHT zu tun oder abzulehnen (z.B. den Verzicht auf bestimmte Genussmittel), nimm diese Verneinung explizit als kontrastierenden Fakt auf.\n"
    "4. Keine Beispiele im Kopf: Nutze kein externes Vorwissen für Standard-Assoziationen (erfinde keine Städte wie Berlin hinzu, wenn sie nicht im Text stehen).\n"
    "5. Wenn eine Kategorie im Text absolut nicht erwähnt wird, setze eine leere Liste [].\n\n"
    
    "Das JSON MUSS exakt folgende Struktur mit diesen exakten Key-Namen haben:\n"
    "{\n"
    "  'kategorie_geografie': ['Liste aller explizit genannten Orte, Städte oder Pendel-Achsen'],\n"
    "  'kategorie_hardware_it': ['Spezifische Geräte, Maschinen, Musikinstrumente, Software und IT-Begriffe'],\n"
    "  'kategorie_kultur_musik': ['Musikgenres, Bands, Künstler, Kunstformen oder ästhetische Vorlieben'],\n"
    "  'kategorie_werte_politik': ['Politische, gesellschaftliche, philosophische Ansichten und Lebenseinstellungen'],\n"
    "  'kategorie_konsum_laster': ['Explizite Gewohnheiten, Laster, Konsumverhalten sowie bewusste Abstanzen (Tabak, Alkohol etc.)'],\n"
    "  'kategorie_freizeit_erholung': ['Aktivitäten, Sehnsuchtsziele oder Tageszeiten, die zur Regeneration genutzt werden']\n"
    "}"
)

# kv_werte = f"Werte: {', '.join(json_data['werte_und_lebenseinstellung'])} | Konsum: {', '.join(json_data['gewohnheiten_und_konsum'])}"
# kv_vibe = f"Kultur: {', '.join(json_data['kulturelle_und_musikalische_dna'])}"
# kv_offenheit = f"Freizeit: {', '.join(json_data['freizeit_und_regeneration'])}"
# kv_komm = f"Hardware: {', '.join(json_data['hardware_technologie_geraete'])} | Orte: {', '.join(json_data['geografischer_anker'])}"

payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Hier ist das Manifest:\n\n{manifest_original}"}
    ],
    "stream": False,
    "format": "json", # DAS zwingt Ollama zu 100% validem JSON
    "options": {
        "temperature": 0.0 # Maximale Fakten-Treue, null Kreativität
    }
}

print(f"🚀 Sende Manifest an lokalen Ollama-Server ({MODEL_NAME})...")
start_time = time.time()

try:
    response = requests.post(OLLAMA_URL, json=payload)
    response_json = response.json()
    
    # Der generierte Text von Ollama
    raw_output = response_json['message']['content']
    
    # Parsen für die schöne Darstellung im Terminal
    parsed_profile = json.loads(raw_output)
    
    print(f"🟩 Extraktion abgeschlossen in {time.time() - start_time:.2f} Sekunden.\n")
    print("=" * 75)
    print("🛰️  DIE REINEN ENTTÄUSCHUNGSFREIEN NUANCEN (PROFIL-SPECKBRIEF):")
    print("=" * 75)
    print(json.dumps(parsed_profile, indent=2, ensure_ascii=False))
    print("=" * 75)

except Exception as e:
    print(f"❌ Fehler bei der Kommunikation mit Ollama: {e}")
    print("💡 Tipp: Läuft Ollama im Hintergrund? Hast du 'ollama run llama3.1' ausgeführt?")