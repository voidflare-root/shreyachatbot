import telebot
import requests
import time
import io
from urllib.parse import quote

# --- CONFIGURATION ---
BOT_TOKEN = '8510711613:AAE9iRWAhlsdDhX3SvjSzURxFtqGOFrD86I'
GROQ_API_KEY = 'GROQ_API_KEY'

bot = telebot.TeleBot(BOT_TOKEN)
user_history = {}

# Shreya ki Personality (Short & Sweet)
SYSTEM_PROMPT = (
    "Your name is Shreya. You are the user's girlfriend. "
    "Talk in Hinglish. Reply in only 1 SHORT line. "
    "Be romantic and sweet. Never say you are an AI."
)

# --- PHOTO GENERATE AUR SEND KARNE KA FUNCTION ---
def send_shreya_photo(chat_id):
    # Ek realistic Indian girl ka prompt
    prompt = (
        "A realistic selfie of a beautiful 20 year old Indian girl, "
        "cute face, smiling, long black hair, natural skin tone, "
        "looking at camera, indoor lighting, high quality."
    )
    encoded = quote(prompt)
    seed = int(time.time()) # Har baar alag photo ke liye
    img_url = f"https://pollinations.ai/p/{encoded}?width=1080&height=1350&seed={seed}&model=flux"
    
    try:
        # Photo ko internet se download karna
        response = requests.get(img_url)
        if response.status_code == 200:
            # Photo ko memory mein save karke Telegram par bhejna (Ye link nahi dikhayega)
            photo_bytes = io.BytesIO(response.content)
            bot.send_photo(chat_id, photo_bytes, caption="Kaisi lag rahi hoon? ❤️ Sharma gayi main toh! 🙈")
        else:
            bot.send_message(chat_id, "Sorry baby, photo click nahi ho paayi.. 🥺")
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(chat_id, "Net issue hai jaan, photo nahi ja rahi.. 🥺")

# --- CHAT FUNCTION ---
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
        res = requests.post(url, json=payload, headers=headers)
        return res.json()['choices'][0]['message']['content']
    except:
        return "Net slow hai jaan.. 🥺"

# --- HANDLERS ---
@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    text = message.text.lower()
    uid = message.chat.id

    # Check agar user photo mang raha hai
    photo_keywords = ["photo", "pic", "selfie", "image", "dikhao", "bhejo"]
    if any(w in text for w in photo_keywords) and ("apni" in text or "teri" in text or "selfie" in text):
        bot.send_message(uid, "Ruko jaan, apni ek pyari si photo bhejti hoon... 😘")
        bot.send_chat_action(uid, 'upload_photo')
        send_shreya_photo(uid) # Photo bhejane wala function
        return

    # Normal Chat
    bot.send_chat_action(uid, 'typing')
    reply = get_chat_response(uid, message.text)
    bot.reply_to(message, reply)

print("Shreya is Online! Ab ye link nahi, seedha photo bhejegi. ❤️")
bot.infinity_polling()
