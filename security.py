import os
import hashlib
import re
import html
import streamlit as st
from cryptography.fernet import Fernet

def get_cipher():
    # Holt den Key aus der .env deines TST-Ordners
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        st.error("🚨 KRITISCHER FEHLER: ENCRYPTION_KEY fehlt in der .env!")
        st.stop()
    return Fernet(key.encode())

def encrypt_data(data):
    if not data: return ""
    return get_cipher().encrypt(data.encode()).decode()

def decrypt_data(token):
    if not token or token == "[Entschlüsselungsfehler]": return token
    try:
        return get_cipher().decrypt(token.encode()).decode()
    except Exception:
        return "[Entschlüsselungsfehler]"

def sanitize_input(text):
    if not text: return ""
    # Schutz gegen XSS und einfache Injektionen
    clean = re.sub(r"(DROP TABLE|DELETE FROM|<script|system\()", "[REDACTED]", text, flags=re.IGNORECASE)
    return html.escape(clean)

def hash_key(vibe_key):
    return hashlib.sha256(vibe_key.encode()).hexdigest()