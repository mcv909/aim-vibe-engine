import torch
from sentence_transformers import SentenceTransformer, models
from transformers import AutoModel, AutoConfig
import numpy as np
import logging

# Stille die Warnungen für ein sauberes Terminal
logging.getLogger("transformers").setLevel(logging.ERROR)

# --- 🛰️ AIM SETUP (Identisch zum Worker) ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'
# logic_enforcer = "Instruct: Represent this person's core identity for personality matching.\nQuery: "
# 🛰️ DER KORREKTE ENFORCER (ChatML-Format) 04.05. ergebnis: RESIDENZ-SCORE: 0.3829
# logic_enforcer = "<|im_start|>system\nRepresent this person's core identity. Focus on facts (Lützow, IT, 303, Techno).<|im_end|>\n<|im_start|>user\n"
# NEUER EXPERIMENTELLER ENFORCER aufgenommen am 04.05 und auch raugenommen ergebniss: RESIDENZ-SCORE: 0.4746
# logic_enforcer = "Instruct: Extract the core biographical facts, specific interests (like techno, 303, photography), and fundamental values from this text for a factual similarity check. Ignore the linguistic style.\nQuery: "
# neuer leerer logic enforcer 04.05. und auch wieder rausgenommen ergebnis. RESIDENZ-SCORE: 0.2555
# logic_enforcer = ""
# neuer logic enforcer - dieses mal im anderen format ergebnis: RESIDENZ-SCORE: 0.3990
# logic_enforcer = "<|im_start|>system\nRepresent this person's core identity for personality matching. Focus on facts (Lützow, IT, 303, Techno).<|im_end|>\n<|im_start|>user\n"
# Option 1: Der „Entitäten-Fokussierer“ > RESIDENZ-SCORE: 0.4778
# logic_enforcer = "Instruct: Identify and represent only the specific entities, locations, technologies, and political values in this text. Completely disregard syntax, tone, and emotional expression for the embedding.\nQuery: "
# Option 2: Der „Profiling-Experte“ > RESIDENZ-SCORE: 0.4733
# logic_enforcer = "Instruct: As a data analyst, convert this personal manifesto into a high-dimensional factual profile. Focus 100% on biographical data and interests. Ignore the writing style.\nQuery: "
# Option 3: Der „Struktur-Zwang“ (ChatML) > RESIDENZ-SCORE: 0.4076
# logic_enforcer = "<|im_start|>system\nYou are a factual feature extractor. Your goal is to represent the person's core data (IT, Lützow, 303, Techno, Links) while being blind to linguistic style.<|im_end|>\n<|im_start|>user\n"
# Der „X-Ray“-Ansatz (Vorschlag für heute Abend) > RESIDENZ-SCORE: 0.5480
# logic_enforcer = "Instruct: Convert the following text into a comma-separated list of raw data points: [Location, Job, Music Genres, Hardware, Political Orientation, Habits]. Remove all fill words, emotions, and sentence structures. Only represent the raw data points in the embedding.\nQuery: "
# Der „Semantic Shredder“ (Radikale Entkleidung) > RESIDENZ-SCORE: 0.6121
# logic_enforcer = "Instruct: Act as a semantic de-noiser. Strip the following text of all stylistic, rhetorical, and emotional elements. Represent ONLY the underlying factual database: locations, specific technologies (303), core interests, and political orientations. The resulting vector must be blind to prose and focus 100% on data points.\nQuery: "
# Der „Structural DNA-Scanner“ (ChatML-Variante) > RESIDENZ-SCORE: 0.5175
# logic_enforcer = "<|im_start|>system\nYou are a high-dimensional feature extractor. Your task is to map personal texts into a rigid coordinate system of facts. Ignore the narrator's voice. Focus on: Lützow, IT, 303, Techno, Left-wing, Photography. If a fact is present, lock the vector to it. Style is noise.<|im_end|>\n<|im_start|>user\n"
# Der „Zero-Style Enforcer“ > RESIDENZ-SCORE: 0.4489
# logic_enforcer = "Instruct: Convert this text into a cold, factual representation of identity markers. Disregard all linguistic style, sentence structure, and emotional tone. Match only the raw semantic entities.\nQuery: "
# Option 7: Der „Entity-Only-Executioner“ > RESIDENZ-SCORE: 0.5327
logic_enforcer = "Instruct: Completely ignore that this is a prose text. Treat the input as a bag of raw data points. Extract and represent ONLY the following categories: Technical hardware (303), exact locations (Lützow), professional field (IT), and political leanings (links). Any linguistic flair, emotion, or narrative structure must be erased from the vector representation for this embedding. Query: "

print(f"🚀 Initialisiere {model_id} auf {device}...")

# Konfiguration mit dem Rope-Theta-Fix
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0 
config.use_cache = False 

# Modell-Struktur wie im Worker aufbauen
transformer_model = AutoModel.from_pretrained(model_id, config=config, trust_remote_code=True)
word_embedding_model = models.Transformer(model_id)
word_embedding_model.auto_model = transformer_model
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model], device=device)

def get_similarity(text1, text2):
    """Berechnet die Cosinus-Ähnlichkeit zwischen zwei Texten."""
    # Enkodierung inklusive Logic Enforcer
    print(f"DEBUG: Nutze Enforcer: '{logic_enforcer}'")
    v1 = model.encode(logic_enforcer + text1 + "<|im_end|>")
    v2 = model.encode(logic_enforcer + text2 + "<|im_end|>")
    
    # Mathematische Cosinus-Ähnlichkeit
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- 🧬 DEINE MANIFESTE ---
# Hier kopierst du deine Texte rein:
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

manifest_test = """Wenn ich ehrlich bin, läuft bei mir eigentlich immer irgendwas. Musik ist kein Bewusstseinszustand bei mir, sie ist einfach da. Der Kern ist elektronisch – Techno, Acid, Drum & Bass, Minimal – und das ist keine Phase, das ist Haltung. Eine kreischende 303 über einem fetten Bass mit einer Melodie die sich irgendwo dazwischenschiebt: mehr brauche ich nicht um einen Abend als gelungen zu betrachten. Dass ich auch mit Sting oder Led Zeppelin oder NIN was anfangen kann, erwähne ich nur der Vollständigkeit halber. Das Herzstück ist und bleibt das Elektronische. Ich drehe selbst gelegentlich an Reglern – nichts für die Öffentlichkeit, aber der Prozess macht mir was. Wenn die Muse da ist. Manchmal ist sie das.
Ich hab mir meinen Lebensort bewusst ausgesucht. Lützow ist kein Kompromiss, das ist Absicht. Vorher Rostock, und der Grund für beides ist derselbe: Wasser. Meer. Diese Möglichkeit, einfach raus zu gehen und auf etwas zu schauen, das größer ist als der eigene Kopf. Gleichzeitig pendle ich nach Frankfurt wenn die Arbeit es verlangt – IT, also meistens remote, manchmal nicht. Dieser Wechsel zwischen Großstadt und dem kleinen Ort hier ist für mich kein notwendiges Übel, das ist ein aktiv genutzter Kontrast. Hamburg liegt auf der Strecke und ich mag Hamburg, das sei noch gesagt.
Unterwegs bin ich gern – zu Fuß, mit dem Rad, nachts durch eine Stadt ohne bestimmtes Ziel. Am Strand sitzen und aufs Meer starren ohne dabei irgendetwas leisten zu müssen ist für mich keine verschwendete Zeit. Das ist eigentlich die direkteste Form von Erholung, die ich kenne.
Ich fotografiere wenn die Zeit es zulässt. Menschen, Straßen, Momente die sich ergeben. Kein Studio, kein Setup.
Politisch bin ich links verortet. Das ist keine große Ansage, das ist einfach wie ich die Welt lese. Ob ich drüber reden will hängt von der Person und dem Moment ab – ich find das Thema wichtig, aber ich muss nicht bei jedem Abend damit anfangen.
Alkohol ist bei mir so gut wie kein Thema. Rauchen leider schon – kein Tabak, IQOS, was ich selbst nicht als Verbesserung verkaufen würde, nur als weniger aggressiv für die Umgebung. Ich weiß es, ich hab's akzeptiert, vorerst."""


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔎 DIREKT-VERGLEICH: ORIGINAL VS. TEST")
    print("="*60)
    
    if "HIER" in manifest_original or "HIER" in manifest_test:
        print("❌ FEHLER: Du musst deine Texte erst in das Script kopieren!")
    else:
        score = get_similarity(manifest_original, manifest_test)
        
        print(f"RESIDENZ-SCORE: {score:.4f}")
        print("-" * 60)
        
        if score > 0.90:
            print("🟩 Ergebnis: Fast identisch. Die KI hat den Kern perfekt behalten.")
        elif score > 0.80:
            print("🟨 Ergebnis: Gute Ähnlichkeit, aber stilistische Abweichungen.")
        else:
            print("🟥 Ergebnis: Massive Dissonanz. Das Modell sieht hier zwei verschiedene Menschen.")
            print("💡 Tipp: Prüfe, ob die AI-Umschreibung zu viele Keywords gelöscht hat.")
    print("="*60 + "\n")