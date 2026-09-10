import json
import os
from datetime import datetime

import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi. .env faylini tekshiring.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LOG_FILE = os.path.join(DATA_DIR, "messages.jsonl")
os.makedirs(DATA_DIR, exist_ok=True)

# Har bir foydalanuvchining hozirgi holati (nima yozayotgani): "complaint" | "suggestion" | "contact" | None
user_state = {}

BTN_COMPLAINT = "📩 Shikoyat"
BTN_SUGGESTION = "💡 Taklif"
BTN_CONTACT = "☎️ Admin bilan bog'lanish"
BTN_CANCEL = "⬅️ Bekor qilish"

REMINDERS = {
    "complaint": (
        "📩 <b>Shikoyat bo'limi</b>\n\n"
        "Qanday va qaysi do'konning ustidan shikoyatingiz bo'lsa, "
        "batafsil ma'lumotlar bilan yozing — biz uni bartaraf etishimiz oson bo'lishi uchun.\n\n"
        "Rahmat!"
    ),
    "suggestion": (
        "💡 <b>Taklif bo'limi</b>\n\n"
        "Biz har qanday takliflaringizga ochiqmiz! "
        "Fikr-mulohaza yoki taklifingizni shu yerga yozib qoldiring."
    ),
    "contact": (
        "☎️ <b>Admin bilan bog'lanish</b>\n\n"
        "Ismingiz, telefon raqamingiz va murojaat sababingizni yozib qoldiring.\n"
        "Tez orada admin siz bilan bog'lanadi."
    ),
}

THANKS = {
    "complaint": "✅ Shikoyatingiz qabul qilindi. Tez orada ko'rib chiqamiz. Rahmat!",
    "suggestion": "✅ Taklifingiz uchun rahmat! Fikringiz biz uchun muhim.",
    "contact": "✅ Ma'lumotlaringiz qabul qilindi. Tez orada admin siz bilan bog'lanadi. Rahmat!",
}

ADMIN_LABELS = {
    "complaint": "🔴 Yangi SHIKOYAT",
    "suggestion": "🟢 Yangi TAKLIF",
    "contact": "🟡 Admin bilan bog'lanish so'rovi",
}


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_COMPLAINT, BTN_SUGGESTION)
    kb.row(BTN_CONTACT)
    return kb


def cancel_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_CANCEL)
    return kb


def save_entry(kind, message):
    user = message.from_user
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "type": kind,
        "user_id": user.id,
        "username": user.username,
        "full_name": (user.first_name or "") + (f" {user.last_name}" if user.last_name else ""),
        "text": message.text,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def notify_admin(kind, entry):
    if not ADMIN_ID:
        return
    username = f"@{entry['username']}" if entry["username"] else "yo'q"
    text = (
        f"{ADMIN_LABELS[kind]}\n\n"
        f"👤 Ism: {entry['full_name'] or '-'}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: <code>{entry['user_id']}</code>\n"
        f"🕒 Vaqt: {entry['time']}\n\n"
        f"✉️ Xabar:\n{entry['text']}"
    )
    try:
        bot.send_message(ADMIN_ID, text)
    except telebot.apihelper.ApiException:
        pass


@bot.message_handler(commands=["start", "menu"])
def handle_start(message):
    user_state.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "🏗 <b>Qurilish Mollari Market</b> botiga xush kelibsiz!\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=main_menu(),
    )


@bot.message_handler(func=lambda m: m.text == BTN_CANCEL)
def handle_cancel(message):
    user_state.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Bekor qilindi.", reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == BTN_COMPLAINT)
def handle_complaint_menu(message):
    user_state[message.chat.id] = "complaint"
    bot.send_message(message.chat.id, REMINDERS["complaint"], reply_markup=cancel_menu())


@bot.message_handler(func=lambda m: m.text == BTN_SUGGESTION)
def handle_suggestion_menu(message):
    user_state[message.chat.id] = "suggestion"
    bot.send_message(message.chat.id, REMINDERS["suggestion"], reply_markup=cancel_menu())


@bot.message_handler(func=lambda m: m.text == BTN_CONTACT)
def handle_contact_menu(message):
    user_state[message.chat.id] = "contact"
    bot.send_message(message.chat.id, REMINDERS["contact"], reply_markup=cancel_menu())


@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_free_text(message):
    kind = user_state.get(message.chat.id)
    if not kind:
        bot.send_message(
            message.chat.id,
            "Iltimos, quyidagi menyudan kerakli bo'limni tanlang 👇",
            reply_markup=main_menu(),
        )
        return

    entry = save_entry(kind, message)
    notify_admin(kind, entry)
    user_state.pop(message.chat.id, None)
    bot.send_message(message.chat.id, THANKS[kind], reply_markup=main_menu())


def run_polling():
    import time

    print("Bot polling ishga tushdi...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"Polling xatosi, 5 soniyadan keyin qayta urinib ko'ramiz: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import threading

    from flask import Flask

    web = Flask(__name__)

    @web.route("/")
    def health():
        return "Qurilish Mollari Market bot ishlab turibdi ✅"

    threading.Thread(target=run_polling, daemon=True).start()

    port = int(os.getenv("PORT", 10000))
    web.run(host="0.0.0.0", port=port)
