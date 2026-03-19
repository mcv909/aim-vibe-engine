from PIL import Image
import os

def optimize():
    input_path = "log_transparent.png"
    output_path = "log_transparent.png"
    
    if os.path.exists(input_path):
        img = Image.open(input_path)
        # Größe anpassen (max 500px Breite reicht völlig)
        img.thumbnail((500, 500))
        # Als PNG speichern
        img.save(output_path, "PNG", optimize=True)
        print(f"✅ Logo optimiert: {os.path.getsize(output_path) / 1024:.2f} KB")
    else:
        print("❌ logo.jpg nicht gefunden!")

if __name__ == "__main__":
    optimize()