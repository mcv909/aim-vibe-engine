import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import logging

# Warnungen stummschalten für sauberen Terminal-Output
logging.getLogger("transformers").setLevel(logging.ERROR)

# --- 🛰️ AIM SETUP ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = "Qwen/Qwen2-1.5B-Instruct"

print(f"🚀 Initialisiere Generative Engine ({model_id}) auf [{device.upper()}]...")
start_load = time.time()

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto").to(device)

print(f"🟩 Modell in {time.time() - start_load:.2f} Sekunden geladen.")

# --- 🧬 DEIN KOHLENSTOFF-ORIGINAL ---
manifest_original = """Liebe Musik, die ist eigentlich ständig um mich. Ich bevorzuge hier Techno bzw. elektronische Musik. Bin aber dahingehend offen und höre auch gerne mal Rock oder Pop (Sting, Police, Led Zeppelin, NIN etc.).
Aber am liebsten eben elektronische Musik, absoluter Faible für Drum n Bass/Jungle, Minimal und eben Techno und Acid.
Es gibt kein geileres geräusch als eine geil kreischende 303 - noch ein fetter Bass dazu und ne schön dahindüdelnde Melodie > BÄM bin glücklich :)
Drehe gerne mal etwas an Potis herum, mache, für mich, auch gerne mal, mit der entsprechende Muse, elektronische Musik.
Genieße aber auch gerne mal die Einsamkeit und die Ruhe im Wald und, vor allem, am Meer. Deswegen verschlug es mich auch nach, erst Rostock, dann jetzt Lützow.
Pendle zwischen Ffm Bankstadt wo ich arbeite (wenn ich vor Ort sein muss) oder eben Lützow in der selbst ausgesuchten Homebase.
Der switch zwischen Großstadt und kleinem Ort ist toll, immer etwas anderes und spannend. Bin auch gerne mal in Hamburg (tolle Stadt).
Ansonsten, wenn es die Zeit zulässst (Arbeite in der IT) fotografiere ich gerne (People und Street).
Ich bin eher links eingestellt, Politik ist wichtig wenn auch nicht immer das beste Thema - muss man Bock drauf haben.
Trinke so gut wie keinen Alkohol aber rauchen ist leider ein aktuell noch bestehendes Laster (keine Kippen, Iqos, aber ist auch nicht viel besser, stinkt wenigstens nicht so).
Spazieren gehen, Biken, am Strand sitzen und sinnfrei aufs Meer starren, das finde ich großartig. Nachts durch eine Stadt wandern, auch toll."""

# --- 🛰️ DER EXTRAKTIONS-PROMPT ---
# Hier zwingen wir die KI, den Stil komplett zu ignorieren und die nackten Nuancen zu listen.
system_prompt = (
    "Du bist ein radikal präziser Fakten-Extractor für ein Matchmaking-System. "
    "Deine Aufgabe ist es, das Manifest des Users in ein starres Datenblatt zu übersetzen.\n"
    "STRIKTE REGEL: Nutze AUSSCHLIESSLICH konkrete Fakten, Eigennamen und Begriffe, die DIREKT im Text stehen. "
    "Erfinde NIEMALS eigene Kategorisierungen oder generische Phrasen (wie 'Computer', 'Sonne', 'Toleranz'). "
    "Wenn zu einer Kategorie kein expliziter Fakt im Text steht, antworte mit 'Nicht genannt'.\n\n"
    "Gib Antworten für folgende 6 Kategorien aus. Nutze exakt dieses Format:\n"
    "1. GEOGRAFISCHER ANKER: (Nur konkret im Text genannte Städte/Orte extrahieren)\n"
    "2. CORE TECHNOLOGY & HARDWARE: (Spezifische Geräte, Maschinennamen oder IT-Begriffe aus dem Text)\n"
    "3. MUSIKALISCHE DNA: (Nur die exakt genannten Subgenres und Künstler aufmisten)\n"
    "4. POLITISCHER KOMPASS: (Die exakte politische Selbstverortung aus dem Text übernehmen)\n"
    "5. GENUSSMITTEL & LASTER: (Den exakten Status zu Alkohol und Rauchen/IQOS spiegeln)\n"
    "6. ERHOLUNGS-TYPUS: (Konkrete Orte und Tageszeiten der Regeneration aus dem Text extrahieren)\n\n"
    "Keine Einleitung, kein Bla-Bla. Nur die harten Text-Fakten."
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Hier ist das Manifest:\n\n{manifest_original}"}
]

# Chat-Template von Qwen anwenden (baut die korrekten ChatML-Tags wie <|im_start|> im Hintergrund)
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
model_inputs = tokenizer([text], return_tensors="pt").to(device)

print("\n🔎 Starte tiefenpsychologische Fakten-Extraktion...")
start_gen = time.time()

# Text generieren
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512,
    temperature=0.1, # Extrem niedrig halten für maximale Fakten-Treue ohne Halluzinationen
    do_sample=False,
    repetition_penalty=1.2  # <-- Zwingt das Modell, neue Begriffe zu nutzen oder aufzuhören
)

# Output dekomprimieren
generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(f"🟩 Extraktion abgeschlossen in {time.time() - start_gen:.2f} Sekunden.\n")
print("=" * 75)
print("🛰️  DIE REINEN NUANCEN (DEIN NEUES EMBEDDING-FUTTER):")
print("=" * 75)
print(response)
print("=" * 75)