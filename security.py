import os
import re
import html
import base64
import hashlib
import streamlit as st
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

def encrypt_for_worker(cleartext, public_key_pem):
    """Verschlüsselt das Manifesto hybrid (RSA + AES)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    import os
    import base64

    # 1. AES Key (32 Bytes = 256 Bit) & IV generieren
    aes_key = os.urandom(32) # WICHTIG: Rohdaten, kein Base64! [cite: 2026-03-04]
    iv = os.urandom(16)
    
    # 2. Manifesto mit AES (CFB Mode) verschlüsseln
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_manifesto = encryptor.update(cleartext.encode()) + encryptor.finalize()
    
    # 3. Den rohen AES-Key mit RSA verschlüsseln
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode() if isinstance(public_key_pem, str) else public_key_pem
    )
    encrypted_aes_key = public_key.encrypt(
        aes_key, # Hier gehen jetzt exakt 32 Bytes rein
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 4. Paket packen: RSA (256 Bytes) + IV (16 Bytes) + Ciphertext
    package = encrypted_aes_key + iv + encrypted_manifesto
    return base64.b64encode(package).decode('utf-8')

# Initialisierung des Argon2-Hashers
ph = PasswordHasher()

# --- 1. KEY-PROTECTION (Hashing) ---
def hash_key(vibe_key):
    """Erzeugt einen sicheren Argon2-Einweg-Hash des Keys."""
    if not vibe_key: return None
    return ph.hash(vibe_key)

def verify_key(vibe_key, hashed_key):
    """Vergleicht den Input mit dem Hash in der DB."""
    try:
        return ph.verify(hashed_key, vibe_key)
    except Exception:
        return False

# --- 2. ZERO-KNOWLEDGE ENCRYPTION (AES) ---
def derive_encryption_key(vibe_key):
    """
    Leitet aus dem User-Key einen AES-Schlüssel ab. 
    Ohne diesen exakten Key bleibt das Manifesto Datenmüll [cite: 2026-01-18].
    """
    digest = hashlib.sha256(vibe_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_data(text, vibe_key):
    """Verschlüsselt Daten mit dem User-abgeleiteten Schlüssel."""
    if not text or not vibe_key: return ""
    cipher = Fernet(derive_encryption_key(vibe_key))
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(token, vibe_key):
    """Entschlüsselt Daten. Falls Key falsch: 'Weg ist weg' [cite: 2026-01-18]."""
    if not token or not vibe_key: return ""
    try:
        cipher = Fernet(derive_encryption_key(vibe_key))
        return cipher.decrypt(token.encode()).decode()
    except Exception:
        return "[Entschlüsselung unmöglich - Key inkorrekt]"

# --- 3. ATTACK DETECTION & SANITIZATION ---
def sanitize_input(text):
    """Basis-Bereinigung für harmlose Felder."""
    if not text: return ""
    return html.escape(text.strip())

def detect_attack(input_string):
    """
    Sucht nach Injektions-Mustern. Falls gefunden: 'Mudda'-Protokoll.
    """
    if not input_string: return False
    patterns = [
        r"(?i)DROP\s+TABLE", r"(?i)DELETE\s+FROM", r"(?i)SELECT\s+\*",
        r"<script.*?>", r"javascript:", r"(\.\./){2,}", r"system\("
    ]
    for pattern in patterns:
        if re.search(pattern, input_string):
            return True
    return False

def handle_hacker():
    """Der finale Rauswurf mit dem gewünschten Wording [cite: 2026-01-18]."""
    st.error("Hacker? Deine Mudda!")
    st.stop()

# --- 4. WORKER-SPECIFIC HYBRID DECRYPTION ---
def decrypt_for_worker(encrypted_data_b64, private_key_pem):
    """
    Entschlüsselt das vom Server kommende Paket für den lokalen AI-Worker.
    Nutzt RSA zur Key-Übertragung und AES-256 für die Daten.
    """
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    # Paket dekodieren
    package = base64.b64decode(encrypted_data_b64)
    
    # Slicing des Pakets: 
    # RSA-verschlüsselter AES-Key (256 Bytes) | IV (16 Bytes) | Ciphertext
    encrypted_aes_key = package[:256]
    iv = package[256:272]
    ciphertext = package[272:]
    
    # 1. Private Key laden
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode() if isinstance(private_key_pem, str) else private_key_pem,
        password=None
    )
    
    # 2. Den AES-Key mit RSA entschlüsseln
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 3. Das Manifesto mit dem AES-Key entschlüsseln (CFB Mode)
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')

def decrypt_manifesto(encrypted_text, vibe_key):
    """Alias für decrypt_data, um den Sound in der app.py zu bedienen."""
    return decrypt_data(encrypted_text, vibe_key)