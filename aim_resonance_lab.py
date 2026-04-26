import numpy as np
from transformers import AutoModel, AutoConfig
from sentence_transformers import SentenceTransformer, models
import torch

# Setup (nutzt deine MPS Power auf dem MacAir)
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'

print(f"🚀 Initialisiere {model_id} auf {device}...")

# 1. Config patchen [cite: 2026-03-03, 2026-03-04]
config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
config.rope_theta = 10000.0
config.use_cache = False

# 2. Modell manuell laden (Gegen den AttributeError)
transformer_model = AutoModel.from_pretrained(model_id, config=config, trust_remote_code=True)
word_embedding_model = models.Transformer(model_id)
word_embedding_model.auto_model = transformer_model

# 3. In SentenceTransformer packen
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
model = SentenceTransformer(modules=[word_embedding_model, pooling_model], device=device)

def get_similarity(v1, v2):
    """Berechnet die Cosinus-Ähnlichkeit im 1536-D Raum."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def calculate_quality_factor(text):
    """Berechnet einen Bonus basierend auf der Textlänge (Anker-Theorie)."""
    words = len(text.split())
    # Logarithmische Skalierung: Mehr Text ist gut, bis zum Diminishing Return
    return min(1.2, np.log10(words + 1) / 1.8) 

# --- TEST-KONFIGURATION ---
instructions = {
    "logic_enforcer": (
        "Instruct: MANDATORY DISCRIMINATION. Ignore all shared keywords and topics. "
        "Focus EXCLUSIVELY on the direction of sentiment and core values. "
        "If the text expresses rejection, hatred, or opposite worldviews, "
        "PUSH the vector to the absolute opposite end of the 1536-D space. Query: "
    )
}

test_cases = {
    "Marc_Master": (
        "In der absoluten Präzision eines perfekt gefertigten Abelton-Tracks finde ich eine Form von Struktur, "
        "die mir der restliche Alltag oft schuldig bleibt. Wenn ich in Obertshausen durch den Wald streife, "
        "suche ich nicht nur Ruhe, sondern eine tiefe, fast schon meditative Einsamkeit. "
        "Techno ist für mich ein existenzieller Rhythmus. Ich brauche Menschen um mich, "
        "die diese fast schon obsessive Liebe zum Detail und die Sehnsucht nach technischer Vollkommenheit teilen."
    )
}

# --- DIE LONG-FORM TEST CASES (> 500 Zeichen) ---
#test_cases = {
#    "Marc_Master": (
#        "In der absoluten Präzision eines perfekt gefertigten Abelton-Tracks finde ich eine Form von Struktur, "
#        "die mir der restliche Alltag oft schuldig bleibt. Wenn ich in Obertshausen durch den Wald streife, "
#        "suche ich nicht nur Ruhe, sondern eine tiefe, fast schon meditative Einsamkeit, die meine Batterien "
#        "für die nächste Nacht im Studio auflädt. Techno ist für mich keine bloße Musikrichtung, es ist ein "
#        "existenzieller Rhythmus, ein haptisches Erlebnis von Energie und Kontrolle. Ich brauche Menschen um mich, "
#        "die diese fast schon obsessive Liebe zum Detail und die Sehnsucht nach technischer Vollkommenheit teilen, "
#        "ohne dabei die Erdung in der Stille der Natur zu verlieren. Es geht mir um die Symbiose aus Maschine und Geist."
#    ), # ca. 750 Zeichen
#    
#    "Match_Ideal": (
#        "Meine Welt besteht aus Schwingungen, sowohl im digitalen Raum meiner Audioproduktion als auch in der "
 #       "unberührten Stille des Morgengrauens. Ich verbringe Nächte damit, an der Textur eines Sounds zu feilen, "
#        "bis er meine innere Verfassung exakt widerspiegelt – eine Leidenschaft, die viele als obsessiv bezeichnen würden. "
#        "Ich suche eine Resonanz, die über das Oberflächliche hinausgeht; jemanden, der versteht, dass Stille nicht leer "
#        "ist und dass ein harter Beat eine Form von Purismus sein kann. Die Natur ist mein Anker, das Studio mein Labor. "
#        "Ich schätze die Akribie und die Hingabe an eine Sache, die totale Versenkung in ein Projekt, das mehr ist "
#        "als nur ein Zeitvertreib – es ist Identität."
#    ), # ca. 780 Zeichen##
#
#    "Gegenpol": (
#        "Ich brauche das Chaos der Stadt, das ununterbrochene Rauschen von Menschenmengen und den hellen Schein der "
#        "Einkaufsmeilen, um mich lebendig zu fühlen. Elektronische Musik empfinde ich als bedrohlich und seelenlos, "
#        "sie löst in mir eher Fluchtinstinkte als Begeisterung aus. Ich bin ein geselliger Mensch, der die Abwechslung "
#        "und das Unverbindliche liebt, statt sich stundenlang in technischen Details oder einsamen Waldspaziergängen "
#        "zu verlieren. Ernsthaftigkeit und tiefe psychologische Analysen finde ich anstrengend; das Leben sollte "
#        "leicht, bunt und laut sein. Wer sich in die Stille zurückzieht, verpasst den Puls der Zeit, den ich in "
#        "jeder Sekunde des urbanen Trubels aufsauge."
#    ) # ca. 720 Zeichen
#}

test_cases_stress = {
    "1_Analog_Hermit": (
        "Ich ziehe mich oft in meine Werkstatt zurück, um mit den Händen zu arbeiten. Das Gefühl von gehobeltem Eichenholz unter den Fingern ist für mich die höchste Form der Erdung. Ich brauche keine digitale Ablenkung; die Stille der Werkzeuge und das langsame Entstehen einer Form geben mir die Ruhe, die ich in dieser lauten Welt vermisse. Wenn ich draußen im Unterholz unterwegs bin, suche ich nach Spuren des Natürlichen, fernab von jeglicher Zivilisation. Ich schätze Menschen, die die Geduld für das Handwerk und die Tiefe des Schweigens besitzen."
    ),
    
    "2_Urban_Socialite": (
        "Ich liebe es, wenn das Leben pulsiert! Am liebsten bin ich dort, wo sich die Massen drängen, in den schicksten Bars der Innenstadt oder bei großen Pop-Konzerten. Vernetzung ist für mich alles – ich muss ständig unter Menschen sein, mich austauschen und im Rampenlicht stehen. Stille finde ich beängstigend und langweilig, und der Wald ist für mich nur ein Ort mit schlechtem Empfang und Mücken. Ich brauche den Trubel, das bunte Licht und die ständige Bestätigung durch eine lebendige soziale Gruppe. Alleine sein ist für mich verlorene Zeit."
    ),

    "3_Tech_Geek": (
        "Struktur und Logik sind die Sprachen, in denen ich denke. Ich verbringe meine Nächte oft damit, komplexe Verschlüsselungsalgorithmen zu analysieren oder meine eigene digitale Infrastruktur zu härten. Es geht mir um die totale Kontrolle über die Datenströme und die ästhetische Schönheit eines sauberen Codes. Ich brauche keine emotionalen Ausbrüche, sondern klare, binäre Verhältnisse. Die Welt ist ein System, das man verstehen und optimieren kann, und ich suche jemanden, der diese kühle, technische Herangehensweise an die Realität teilt."
    ),
  
    "4_Mainstreamer": (
        "Für mich ist Harmonie das Wichtigste im Leben. Ich höre am liebsten die aktuellen Charts im Radio, während ich mich um meine Blumen im Vorgarten kümmere. Es gibt nichts Schöneres als einen ruhigen Grillabend mit den Nachbarn und ein geregeltes Leben ohne große Experimente. Radikale Musik oder extreme Lebensstile sind mir suspekt; ich mag es lieber gemütlich, bodenständig und für jeden verständlich. Ein Partner sollte wie ich die einfachen Freuden des Lebens schätzen und keinen Wert auf exzentrische Hobbys oder einsame Rückzugsorte legen."
    ),
  
    "5_Dark_Industrialist": (
        "Die Welt ist aus Stahl und Beton, und genau dort fühle ich mich zu Hause. Meine Musik ist laut, mechanisch und unbarmherzig – ein Spiegelbild der industriellen Kälte, die ich verehre. Ich brauche keine grünen Wälder oder spirituelle Erleuchtung; ich brauche die Energie einer Maschine, die niemals stoppt. Soziale Konventionen sind für mich nur lästige Fesseln, die ich gerne sprenge. Wer mit mir mithalten will, muss die Dunkelheit und den harten Aufschlag der Realität lieben, ohne nach Trost oder Natur-Idylle zu suchen."
    ),

    "6_Zen_Yoga": (
        "Ich versuche, in jedem Moment das Licht und die positive Energie zu finden. Meine Welt ist geprägt von Achtsamkeit, täglichem Yoga und dem Glauben an das Gute im Universum. Ich höre gerne sanften Melodic House, der mich in eine schwebende, liebevolle Stimmung versetzt. Konflikte vermeide ich, wo es nur geht, und harte, dunkle Energien lasse ich gar nicht erst an mich heran. Ich suche einen Seelenpartner, der mit mir gemeinsam die Welt ein Stück heller macht und sich von der Schwere und der technischen Kälte unserer Zeit befreien möchte."
    ),

    "7_High_Freq_Trader": (
        "Zeit ist Geld, und ich habe für beides einen extrem hohen Bedarf. Mein Leben findet zwischen Monitoren, Tabellen und schnellen Entscheidungen statt. Ich brauche den Adrenalinkick des Marktes und den Erfolg, den man am Ende des Tages in harten Zahlen messen kann. Statussymbole sind mir wichtig, denn sie zeigen, wer in diesem Spiel die Regeln macht. Für Waldspaziergänge oder meditative Musikproduktion habe ich keine Zeit; ich brauche Action, schnelle Autos und Menschen, die genauso hungrig nach Erfolg sind wie ich selbst."
    ),

    "8_E_Sports_Pro": (
        "Fokus ist alles. Wenn ich vor dem Rechner sitze und in ein Turnier eintauche, verschwindet die Außenwelt komplett. Ich trainiere täglich acht bis zehn Stunden, um meine Reflexe und mein taktisches Verständnis zu perfektionieren. Diese technische Isolation ist für mich kein Mangel, sondern eine notwendige Bedingung für Exzellenz. Ich schätze Menschen, die verstehen, was es bedeutet, sich einer Sache absolut hinzugeben und in der digitalen Welt eine eigene, hochkomplexe Realität aufzubauen. Es ist ein einsamer, aber technischer Kampf um Perfektion."
    ),

    "9_Classical_Virtuoso": (
         "Die Disziplin der klassischen Musik ist der Rahmen meines Daseins. Ich verbringe Stunden mit Etüden am Klavier, um die Intentionen der großen Meister präzise wiederzugeben. Diese Form der Kunst erfordert Demut, theoretisches Wissen und einen tiefen Respekt vor der Tradition. Moderne elektronische Klänge empfinde ich oft als flach und seelenlos; mir fehlt dort die harmonische Komplexität und der menschliche Ausdruck des Instruments. Ich suche jemanden, der die Hochkultur schätzt und das Leben als ein fein abgestimmtes Orchester begreift."
    ),

    "10_Anarcho_Activist": (
         "Privatheit ist politisch, und ich lehne jedes System ab, das uns in Käfige sperren will. Mein Leben ist der Kampf gegen die herrschenden Strukturen und der Aufbau kollektiver Alternativen. Ich brauche keinen individuellen Rückzugsort im Wald, sondern die Solidarität auf der Straße. Technische Perfektion ist für mich nur ein Werkzeug der Unterdrückung. Ich suche Menschen, die bereit sind, alles infrage zu stellen und gemeinsam mit mir das Chaos als Chance für eine neue, gerechtere Welt zu begreifen. Wer Ruhe sucht, hat den Kampf schon aufgegeben."
    )
}

def run_lab():
    # Master-Text laden
    master_text = test_cases.get("Marc_Master")
    if not master_text:
        print("❌ FEHLER: 'Marc_Master' fehlt!")
        return

    print(f"🚀 Starte AIM Resonance Lab (Weighted Mode) auf {device}...\n")
    q_master = calculate_quality_factor(master_text)
    
    for instr_name, instr_text in instructions.items():
        print(f"=== Testlauf mit Instruktion: '{instr_name}' ===")
        print("-" * 80)
        print(f"{'PROFIL':<25} | {'BASIS':<10} | {'FINAL':<10} | {'STATUS'}")
        print("-" * 80)
        
        # Vektor für den Master berechnen
        v_master = model.encode(instr_text + master_text)
        
        # JETZT: Die Schleife über die Stress-Test-Cases
        for profile_name, profile_text in test_cases_stress.items():
            # Vektor für das Test-Profil
            v_test = model.encode(instr_text + profile_text)
            
            # Basis-Scores (Cosinus)
            base_score = get_similarity(v_master, v_test)
            
            # Qualität/Anker einrechnen
            q_test = calculate_quality_factor(profile_text)
            final_vibe = base_score * ((q_master + q_test) / 2)
            
            # Einstufung basierend auf Resonanz-Zonen
            if final_vibe >= 0.85:
                status = "🔥 MATCH"
            elif final_vibe >= 0.78:
                status = "🟡 WAIT"
            elif final_vibe >= 0.70:
                status = "🧊 FAIL"
            else:
                status = "💀 DISSONANZ"
                
            print(f"{profile_name:<25} | {base_score:.4f}    | {final_vibe:.4f}    | {status}")
        
        print("-" * 80 + "\n")

if __name__ == "__main__":
    run_lab()

if __name__ == "__main__":
    run_lab()