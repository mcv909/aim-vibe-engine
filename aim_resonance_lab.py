import numpy as np
from sentence_transformers import SentenceTransformer
# Wir importieren nur die notwendigen Teile deines bestehenden Setups [cite: 2026-03-04]
import torch

# Setup (nutzt deine MPS Power auf dem MacAir) [cite: 2025-12-20]
device = "mps" if torch.backends.mps.is_available() else "cpu"
model_id = 'Alibaba-NLP/gte-Qwen2-1.5B-instruct'
# Hier laden wir das Modell wie im Worker (gekürzt für das Lab)
model = SentenceTransformer(model_id, device=device, trust_remote_code=True)

def get_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- TEST-KONFIGURATION ---
instructions = {
    "keine": "",
    "philosophisch": "Instruct: Identify user profiles that exhibit high personal resonance and shared philosophical worldviews. Query: ",
    "lifestyle": "Instruct: Match users based on shared hobbies and daily energy levels. Query: "
}

test_cases = {
    "Marc_Master": "Ich liebe harten Techno, schraube Nächte lang an Abelton-Projekten und brauche meine Ruhe im Obertshausener Wald.",
    "Match_Ideal": "Techno ist mein Leben, ich produziere selbst Musik und suche jemanden, der auch die Stille der Natur schätzt.",
    "Gegenpol": "Ich hasse laute Musik und hänge lieber in vollen Innenstädten rum. Techno finde ich furchtbar anstrengend."
}

def run_lab():
    print(f"🚀 Starte AIM Resonance Lab auf {device}...\n")
    
    for instr_name, instr_text in instructions.items():
        print(f"=== Testlauf mit Instruktion: '{instr_name}' ===")
        
        # Vektoren berechnen
        v_master = model.encode(instr_text + test_cases["Marc_Master"])
        v_match = model.encode(instr_text + test_cases["Match_Ideal"])
        v_fail = model.encode(instr_text + test_cases["Gegenpol"])
        
        score_match = get_similarity(v_master, v_match)
        score_fail = get_similarity(v_master, v_fail)
        
        print(f"✅ Ideal-Match: {score_match:.4f}")
        print(f"❌ Gegenpol:    {score_fail:.4f}")
        print(f"⚖️ Delta (Abstand): {abs(score_match - score_fail):.4f}")
        
        if score_match > score_fail:
            print("💎 Logik stabil: Match schwingt höher als Fail.")
        else:
            print("⚠️ Logik-Fehler: Der Gegenpol ist mathematisch näher!")
        print("-" * 40)

if __name__ == "__main__":
    run_lab()