import os
import telebot
from datetime import datetime, timedelta
from db_handler import get_connection, delete_profile_permanently

# Bot-Initialisierung
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- 1. DER NOTAUSGANG (Emergency Exit) ---
@bot.message_handler(commands=['delete_dna'])
def handle_delete_request(message):
    """
    Löscht das Profil unwiderruflich ohne Passwort-Abfrage [cite: 2026-01-18].
    """
    tid = message.chat.id
    
    # Bestätigungs-Check (optional, aber sicher)
    markup = telebot.types.InlineKeyboardMarkup()
    item_yes = telebot.types.InlineKeyboardButton("JA, unwiderruflich löschen", callback_data=f"confirm_delete_{tid}")
    item_no = telebot.types.InlineKeyboardButton("Nein, war ein Versehen", callback_data="cancel_delete")
    markup.add(item_yes, item_no)
    
    bot.send_message(tid, "<b>Nachricht empfangen.</b> 🛰️\n\nBist du sicher? Dein Profil wird sofort unsichtbar und alle Daten werden gelöscht.", parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete(call):
    tid = int(call.data.split('_')[2])
    if delete_profile_permanently(tid):
        msg = (
            "<b>Over and out.</b> 🛰️\n\n"
            "Dein Profil wurde gelöscht. Ich gehe mal davon aus, dass die Resonanz im echten Leben gerade spannender ist als meine Vektor-Logik.\n"
            "Euch viel Glück und Spaß, auf dass ihr einen neuen Lieblingsmenschen gefunden habt. Hoffe, wir lesen uns gar nicht wieder! ;)"
        )
        bot.answer_callback_query(call.id, "DNA gelöscht.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg, parse_mode='HTML')
    else:
        bot.send_message(tid, "Fehler beim Löschen. Kontaktiere den Admin: marc.c.vietor@gmail.com")

# --- 2. DIGITALE HYGIENE (Deadman-Ping) ---
def run_deadman_check():
    """
    Sucht nach Profilen, die seit 6 Monaten nicht mehr reagiert haben [cite: 2026-01-18].
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Profile finden, deren created_at oder last_ping über 6 Monate her ist
    six_months_ago = datetime.now() - timedelta(days=180)
    
    try:
        cur.execute("SELECT telegram_id FROM profiles WHERE created_at < %s AND is_active = true", (six_months_ago,))
        stale_users = cur.fetchall()
        
        for user in stale_users:
            tid = user[0]
            msg = (
                "<b>Bist du noch in Resonanz mit uns?</b> 🧬\n\n"
                "Dein Signal bei AIM ist nun seit 6 Monaten stabil. Bitte logge dich innerhalb der nächsten 4 Wochen einmal auf der Website ein, "
                "um dein Profil zu bestätigen. Ansonsten löschen wir deine DNA automatisch, um die Matrix sauber zu halten."
            )
            bot.send_message(tid, msg, parse_mode='HTML')
            # Hier müsste man noch ein Flag 'ping_sent_at' in der DB setzen
            
    finally:
        cur.close()
        conn.close()

# --- 3. STANDARD BEFEHLE ---
@bot.message_handler(commands=['start', 'id'])
def send_id(message):
    user_id = message.chat.id    
    welcome_text = (
        "<b>Willkommen bei [ i am ] | AIM 🎯</b>\n\n"
        "Du hast den ersten Schritt zur Resonanz gemacht.\n"
        f"Deine persönliche Telegram-ID lautet: <code>{user_id}</code>\n\n"
        "Kopiere diese Zahl und füge sie auf der Website ein.\n"
        "Wichtig: Dies ist dein Kontrollzentrum. Nur hier kannst du dein Profil ohne Passwort löschen (/delete_dna)."
    )
    bot.reply_to(message, f"Deine Telegram-ID: <code>{message.chat.id}</code>", parse_mode='HTML')

# Starten des Bots (Polling)
if __name__ == "__main__":
    print("AIM Bot patrouilliert im Äther...")
    bot.infinity_polling()