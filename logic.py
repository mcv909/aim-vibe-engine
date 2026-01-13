import numpy as np
import telebot
import os
import streamlit as st
import math
from geopy.geocoders import Nominatim

def get_coords(location_name):
    """Wandelt Ortsnamen in (Lat, Lon) um."""
    geolocator = Nominatim(user_agent="aim_vibe_engine")
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        return None
    return None

def calculate_distance(coord1, coord2):
    """Berechnet die Entfernung in km via Haversine."""
    if not coord1 or not coord2:
        return 9999 # Strafe für fehlende Daten
    
    R = 6371.0 # Erdradius
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_stature_match(my_stature, target_stature_list, partner_stature, partner_target_list):
    """Prüft, ob die Statur-Wünsche beidseitig passen."""
    # Passt die Statur des Partners in meine Wunschliste?
    i_happy = partner_stature in target_stature_list
    # Passt meine Statur in die Wunschliste des Partners?
    partner_happy = my_stature in partner_target_list
    return i_happy and partner_happy

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