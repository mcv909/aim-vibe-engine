import numpy as np
import telebot
import os
import math
import streamlit as st
import ssl
import certifi
import geopy.geocoders
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from db_handler import get_connection

# SSL-Fix für den Hetzner-Server
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

# Das Werkzeug für alle Geographie-Funktionen
geolocator = Nominatim(user_agent="aim_vibe_resonator_tst_marc")

# --- GEOGRAPHIE ---
def get_coords(location_name):
    """Lokalisiert den User (sollte nur einmalig bei Erstellung genutzt werden)."""
    geolocator = Nominatim(user_agent="aim_vibe_engine")
    try:
        location = geolocator.geocode(location_name)
        return (location.latitude, location.longitude) if location else None
    except Exception: return None

def calculate_distance(coord1, coord2):
    """Berechnet die Haversine-Distanz zwischen zwei Koordinaten."""
    if not coord1 or not coord2: return 9999
    R = 6371.0 
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- MATCHING LOGIK (BATCH) ---
# incl der abfrage ob matches schon vorhanden sind
def run_batch_matching():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Wir nutzen die UUID (id) als internen Anker
        cur.execute("SELECT id, telegram_id, vector_string, coords, stature, target_stature, radius FROM profiles WHERE is_active = true AND is_vectorized = true")
        users = cur.fetchall()
        
        for user in users:
            u_uuid, u_tid, u_vec, u_coords, u_stature, u_target_stature, u_radius = user
            
            # 2. pgvector Suche (Top 10)
            cur.execute("""
                SELECT id, telegram_id, coords, stature, target_stature, (1 - (vector_string <=> %s)) as similarity 
                FROM profiles 
                WHERE id != %s AND is_active = true 
                ORDER BY vector_string <=> %s 
                LIMIT 10
            """, (u_vec, u_uuid, u_vec))
            
            candidates = cur.fetchall()
            
            for cand in candidates:
                c_uuid, c_tid, c_coords, c_stature, c_target_stature, c_sim = cand
                
                # ... (Deine Distanz- und Statur-Checks bleiben hier gleich) ...
                resonance_score = c_sim 
                # (Hier baust du deine Abzüge für Distanz/Statur ein, wie im vorigen Code)

                if resonance_score >= 0.88:
                    # DIE ANTI-SPAM LOGIK:
                    # Wir prüfen, ob dieses Paar schon in der matches-Tabelle steht
                    cur.execute("""
                        SELECT id FROM matches 
                        WHERE (user_a = %s AND user_b = %s) OR (user_a = %s AND user_b = %s)
                    """, (u_uuid, c_uuid, c_uuid, u_uuid))
                    
                    if not cur.fetchone():
                        # Neues Match! Speichern und User pingen
                        cur.execute("""
                            INSERT INTO matches (user_a, user_b, resonance_score) 
                            VALUES (%s, %s, %s)
                        """, (u_uuid, c_uuid, resonance_score))
                        conn.commit()
                        
                        notify_match(u_tid, c_tid, resonance_score)
                        
    finally:
        cur.close()
        conn.close()

# --- TELEGRAM SIGNALE ---
def send_telegram_msg(tid, msg):
    """Sendet eine Nachricht an eine spezifische Telegram-ID."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        try:
            bot = telebot.TeleBot(token)
            bot.send_message(tid, msg, parse_mode='HTML')
        except Exception as e: 
            print(f"Telegram-Fehler bei {tid}: {e}")

def notify_match(tid_a, tid_b, score):
    """Verschickt die 'Live-Notification' bei einem Volltreffer."""
    msg = (
        "<b>Dein individueller String steht.</b> 🧶\n\n"
        "Dein qualitativer Anker hat eine starke Resonanz gefunden! "
        "AIM hat jemanden lokalisiert, dessen Vektoren mit deinen Tango tanzen wollen.\n"
        f"Resonanz-Level: {score:.4f}\n\n"
        "Viel Erfolg beim entspannten Nicht-Suchen."
    )
    send_telegram_msg(tid_a, msg)
    # Optional: Auch tid_b informieren, falls gewünscht

# Und das ist die fehlende Funktion:
def geocode_city(city_name):
    """Verwandelt Stadt/PLZ in [lat, lon] für die Profil-Erstellung."""
    if not city_name: return None
    try:
        # Wir hängen "Germany" an, damit er nicht in Hamburg, Iowa landet
        search_query = f"{city_name.strip()}, Germany"
        location = geolocator.geocode(search_query, timeout=15)
        
        if location:
            print(f"DEBUG: Standort gefunden: {location.address}")
            return [location.latitude, location.longitude]
        return None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None