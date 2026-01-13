import numpy as np
import telebot
import os
import streamlit as st

def calculate_similarity(vec1, vec2):
    """Berechnet die Cosinus-Ähnlichkeit zwischen zwei Vektoren."""
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def is_gender_match(user_gender, user_pref, target_gender, target_pref):
    """
    Prüft, ob zwei Profile basierend auf Geschlecht und Präferenz zusammenpassen.
    Optionen: 'm', 'w', 'd', 'egal'
    """
    # 1. Passt das Ziel-Geschlecht zur Suche des Users?
    user_happy = (user_pref == 'egal') or (user_pref == target_gender)
    
    # 2. Passt das User-Geschlecht zur Suche des Ziel-Profils?
    target_happy = (target_pref == 'egal') or (target_pref == user_gender)
    
    return user_happy and target_happy

def send_telegram_msg(msg, silent=False):
    """Sendet eine Nachricht an den Admin-Bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")
    
    if token and admin_id:
        try:
            bot = telebot.TeleBot(token)
            bot.send_message(
                int(admin_id), 
                msg, 
                parse_mode='Markdown', 
                disable_notification=silent
            )
        except Exception as e:
            st.error(f"Telegram-Fehler: {e}")