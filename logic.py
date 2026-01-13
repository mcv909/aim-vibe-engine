import numpy as np
import telebot
import os
import math
import streamlit as st
from geopy.geocoders import Nominatim

def calculate_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_coords(location_name):
    geolocator = Nominatim(user_agent="aim_vibe_engine")
    try:
        location = geolocator.geocode(location_name)
        return (location.latitude, location.longitude) if location else None
    except Exception: return None

def calculate_distance(coord1, coord2):
    if not coord1 or not coord2: return 999
    R = 6371.0 # Erdradius km
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def is_gender_match(u_g, u_p, t_g, t_p):
    return (u_p == 'egal' or u_p == t_g) and (t_p == 'egal' or t_p == u_g)

def is_stature_match(u_s, u_ts_list, t_s, t_ts_list):
    return (t_s in u_ts_list) and (u_s in t_ts_list)

def send_telegram_msg(msg):
    token, admin_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_ADMIN_ID")
    if token and admin_id:
        try: telebot.TeleBot(token).send_message(int(admin_id), msg, parse_mode='Markdown')
        except Exception as e: st.error(f"Telegram-Fehler: {e}")