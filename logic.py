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
def run_batch_matching(current_user_id=None): # Optionaler Parameter für Einzel-Check
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Wir holen alle aktiven User und ihre Filter-Kriterien
        # Falls current_user_id gesetzt ist, matchen wir nur für einen (Performance!)
        sql_base = """
            SELECT id, telegram_id, vector_string, u_age, u_gender, 
                   u_looking_for, u_age_min, u_age_max, u_intent 
            FROM profiles 
            WHERE is_active = true AND is_vectorized = true
        """
        if current_user_id:
            cur.execute(sql_base + " AND telegram_id = %s", (current_user_id,))
        else:
            cur.execute(sql_base)
            
        users = cur.fetchall()
        
        for user in users:
            u_uuid, u_tid, u_vec, u_age, u_gen, u_look, u_min, u_max, u_int = user
            
            # 2. Die verschärfte pgvector-Suche mit Hard-Filtern
            # Wir prüfen: 
            # - Passt Kandidat in MEIN Raster? 
            # - Passe ICH in das Raster des Kandidaten?
            cur.execute("""
                SELECT id, telegram_id, (1 - (vector_string <=> %s)) as similarity 
                FROM profiles 
                WHERE id != %s 
                AND is_active = true 
                
                -- GATE 1: Passt der Kandidat in MEIN Raster?
                AND u_age BETWEEN %s AND %s                -- Alter
                AND (u_gender = %s OR %s = 'egal')         -- Geschlecht
                AND (u_intent = %s OR u_intent = 'both')   -- Intent
                
                -- GATE 2: Passe ICH in das Raster des Kandidaten? (Reziprozität)
                AND %s BETWEEN u_age_min AND u_age_max     -- Mein Alter in deren Range
                AND (u_looking_for = %s OR u_looking_for = 'egal') -- Mein Geschlecht in deren Suche
                
                ORDER BY similarity DESC 
                LIMIT 15
            """, (u_vec, u_uuid, u_min, u_max, u_look, u_look, u_int, u_age, u_gen))
            
            candidates = cur.fetchall()
            
            for cand in candidates:
                c_uuid, c_tid, c_sim = cand
                
                # Schwellenwert für Vektor-Resonanz
                if c_sim >= 0.88:
                    cur.execute("""
                        SELECT id FROM matches 
                        WHERE (user_a = %s AND user_b = %s) OR (user_a = %s AND user_b = %s)
                    """, (u_uuid, c_uuid, c_uuid, u_uuid))
                    
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO matches (user_a, user_b, resonance_score) 
                            VALUES (%s, %s, %s)
                        """, (u_uuid, c_uuid, c_sim))
                        conn.commit()
                        notify_match(u_tid, c_tid, c_sim)
                        
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