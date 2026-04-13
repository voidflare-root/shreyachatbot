import telebot
import requests
import time
import io
import os
from urllib.parse import quote
from flask import Flask
from threading import Thread

# --- RENDER PORT BINDING (Fix for Port Timeout) ---
app = Flask('')

@app.route('/')
def home():
    return "Shreya is Online! ❤️"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION (Render ke Environment Variables se lega) ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
user_history = {}

# Shreya ki Personality
SYSTEM_PROMPT = (
    "Your name is Shreya. You are the user's girlfriend. "
    "Talk in Hinglish. Reply in only 1 SHORT line. "
    "Be romantic and sweet. Never say you are an AI."
)

# --- PHOTO GENERATE FUNCTION ---
def send_shreya_photo(chat_id):
    prompt = (
        "A realistic selfie of a beautiful 20 year old Indian girl, "
        "cute face, smiling, long black hair, natural skin tone, "
        "looking at camera, indoor lighting, high quality."
    )
    encoded = quote(prompt)
    seed = int(time.time()) 
    img_url = f"https://pollinations.ai/p/{encoded}?width=1080&height=1350&seed={seed}&model=flux"
    
    try:
        response = requests.get(img_url, timeout=20)
        if response.status_code == 200:
            photo_bytes = io.BytesIO(response.content)
            bot.send_photo(chat_id, photo_bytes, caption="Kaisi lag rahi hoon? ❤️ Sharma gayi main toh! 🙈")
        else:
            bot.send_message(chat_id, "Sorry baby, photo click nahi ho paayi.. 🥺")
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(chat_id, "Net issue hai jaan, photo nahi ja rahi.. 🥺")

# --- CHAT FUNCTION (Groq API) ---
def get_chat_response(user_id, text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    if user_id not in user_history:
        user_history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_history[user_id].append({"role": "user", "content": text})
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": user_history[user_id],
        "temperature": 0.8,
        "max_tokens": 70
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        res_data = res.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Net slow hai jaan.. 🥺"

# --- HANDLERS ---
@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    text = message.text.lower()
    uid = message.chat.id

    # Photo Check
    photo_keywords = ["photo", "pic", "selfie", "image", "dikhao", "bhejo"]
    if any(w in text for w in photo_keywords) and ("apni" in text or "teri" in text or "selfie" in text):
        bot.send_message(uid, "Ruko jaan, apni ek pyari si photo bhejti hoon... 😘")
        bot.send_chat_action(uid, 'upload_photo')
        send_shreya_photo(uid)
        return

    # Normal Chat
    bot.send_chat_action(uid, 'typing')
    reply = get_chat_response(uid, message.text)
    bot.reply_to(message, reply)

# --- START BOT ---
if __name__ == "__main__":
    keep_alive() # Flask server start karega Render ke liye
    print("Shreya is Online! ❤️")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
