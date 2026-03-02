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
import base64

def encrypt_for_worker(text, public_key_pem):
    """Hybride Verschlüsselung: Manifesto per AES, AES-Key per RSA."""
    if not text or not public_key_pem: return None
    
    # 1. AES-Key generieren & Manifesto verschlüsseln
    aes_key = Fernet.generate_key()
    cipher_aes = Fernet(aes_key)
    encrypted_text = cipher_aes.encrypt(text.encode())
    
    # 2. RSA Public Key laden & AES-Key verschlüsseln
    pub_key = serialization.load_pem_public_key(public_key_pem.encode())
    encrypted_aes_key = pub_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 3. Paket schnüren: [Verschlüsselter Key]:[Verschlüsseltes Manifesto]
    # Das Format muss dein Worker (aim_worker.py) später wieder trennen können!
    package = base64.b64encode(encrypted_aes_key).decode() + ":" + encrypted_text.decode()
    return package

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