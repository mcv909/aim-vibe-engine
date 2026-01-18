import numpy as np
import telebot
import os
import math
import streamlit as st
from geopy.geocoders import Nominatim
from db_handler import get_connection

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
def run_batch_matching():
    """
    Das Herzstück: Scannt die Matrix nach Resonanzen.
    Wird periodisch im Hintergrund ausgeführt.
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=None) # Wir nutzen Standard-Cursor für Vektor-Input
    
    try:
        # 1. Hole alle aktiven und vektorisierten Profile
        cur.execute("SELECT id, telegram_id, vector_string, coords, stature, target_stature, radius FROM profiles WHERE is_active = true AND is_vectorized = true")
        users = cur.fetchall()
        
        for i, user in enumerate(users):
            u_id, u_tid, u_vec, u_coords, u_stature, u_target_stature, u_radius = user
            
            # 2. Nutze pgvector für die semantische Suche (Top 10 Kandidaten)
            # 1 - (vector_string <=> %s) berechnet die Cosine Similarity
            cur.execute("""
                SELECT id, telegram_id, coords, stature, target_stature, (1 - (vector_string <=> %s)) as similarity 
                FROM profiles 
                WHERE id != %s AND is_active = true 
                ORDER BY vector_string <=> %s 
                LIMIT 10
            """, (u_vec, u_id, u_vec))
            
            candidates = cur.fetchall()
            
            for cand in candidates:
                c_id, c_tid, c_coords, c_stature, c_target_stature, c_sim = cand
                
                # --- RESONANZ SCORING ---
                # Gewichte: Similarity (1.0), Distance (0.5), Stature (0.3)
                dist = calculate_distance(u_coords, c_coords)
                
                # Soft-Filter: Radius-Flexibilität von 20%
                effective_radius = u_radius * 1.2
                
                # Statur-Match prüfen
                stature_match = (c_stature in u_target_stature) and (u_stature in c_target_stature)
                
                # Kombinierter Score (vereinfacht für v0.7.6)
                # Ein extrem hoher Vektor-Score kann Distanz-Mängel ausgleichen
                resonance_score = c_sim
                if dist > effective_radius: resonance_score -= 0.1 # Strafe für Distanz
                if not stature_match: resonance_score -= 0.1       # Strafe für Statur
                
                # Benachrichtigungs-Threshold
                if resonance_score >= 0.88:
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