import os
import sqlite3
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG - Safe Version (GitHub Secret se lega) ---
BOT_TOKEN = os.getenv("9139073932:AAGBSgnkzrhzkYp08PfSWLpxmgJCqhc83EE") 
CHAT_ID = os.getenv("CHAT_ID") or "6165763871"
OPENAI_API_KEY = os.getenv("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")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
active_work_orders = {}

def init_enterprise_db():
    conn = sqlite3.connect("agent_ultimate_core.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completed_works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_type TEXT,
            requirement TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_professional_files(skill_type, content_text):
    safe_title = skill_type.lower().replace("/", "_").replace(" ", "_")
    txt_filename = f"{safe_title}_deliverable.txt"
    docx_filename = f"{safe_title}_deliverable.docx"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"PROJECT CATEGORY: {skill_type}\nSTATUS: FINAL DELIVERABLE\n{'='*50}\n\n{content_text}")
    with open(docx_filename, "w", encoding="utf-8") as f:
        f.write(f"--- CLIENT SUBMISSION FRAMEWORK ---\nCategory: {skill_type}\n\n{content_text}")
    return txt_filename, docx_filename

def ai_work_executor(skill_type, user_prompt):
    base_anti_ai_instruction = (
        "Strict Rule: You must act as a premium human freelance expert with years of industry experience. "
        "Do not include any preambles, greetings like 'Here is your script', or conversational filler. "
        "Deliver only the raw, polished, production-ready final asset."
    )
    if skill_type == "Content Writing":
        system_prompt = f"{base_anti_ai_instruction} Write a flawless piece on: '{user_prompt}'"
    elif skill_type == "Script Writing":
        system_prompt = f"{base_anti_ai_instruction} Act as elite Screenwriter for: '{user_prompt}'"
    elif skill_type == "Instagram Reels/Shorts":
        system_prompt = f"{base_anti_ai_instruction} Write viral short-form script for: '{user_prompt}'"
    elif skill_type == "Web Designing":
        system_prompt = f"{base_anti_ai_instruction} Senior UI/UX engineer. Write clean Tailwind HTML for: '{user_prompt}'. Only code."
    else:
        system_prompt = f"You are master Creative Director. Detailed visual layout for: '{user_prompt}'. No watermarks."

    try:
        # FIXED URL - tera wala galat tha
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.65
        }
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        if res.status_code == 200:
            output = res.json()['choices'][0]['message']['content'].strip()
            return output
        else:
            return f"❌ OpenAI API Error {res.status_code}: {res.text[:200]}"
    except Exception as e:
        return f"❌ System Error: {e}"

def generate_professional_graphic(prompt_text, skill_type):
    try:
        url = "https://api.openai.com/v1/images/generations"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        style_modifier = "Cinematic studio photography, high-end commercial layout, perfectly clean vector, ultra-sharp focus, no watermarks, no logos."
        payload = {
            "model": "dall-e-3",
            "prompt": f"{skill_type} asset: {prompt_text}. Style: {style_modifier}",
            "n": 1,
            "size": "1792x1024" if skill_type == "YouTube Thumbnail" else "1024x1792"
        }
        res = requests.post(url, json=payload, headers=headers, timeout=40)
        if res.status_code == 200:
            return res.json()['data'][0]['url']
    except Exception:
        pass
    return None

@bot.message_handler(commands=['dowork'])
def ask_for_work(message):
    if str(message.chat.id) != str(CHAT_ID): return
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📝 Content Writing", callback_data="do_Content Writing"),
               InlineKeyboardButton("📜 Script Writing", callback_data="do_Script Writing"))
    markup.row(InlineKeyboardButton("🌐 Web Designing", callback_data="do_Web Designing"),
               InlineKeyboardButton("🎬 Instagram Reels", callback_data="do_Instagram Reels/Shorts"))
    markup.row(InlineKeyboardButton("🖼️ YouTube Thumbnail", callback_data="do_YouTube Thumbnail"),
               InlineKeyboardButton("📸 Instagram Story", callback_data="do_Instagram Story"))
    bot.send_message(CHAT_ID, "💼 **HUMAN FREELANCE WORK ENGINE ACTIVE**\n\nKaun sa kaam karwana hai?", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("do_"))
def handle_work_selection(call):
    if str(call.message.chat.id) != str(CHAT_ID): return
    skill = call.data.replace("do_", "")
    active_work_orders[str(CHAT_ID)] = skill
    bot.edit_message_text(chat_id=CHAT_ID, message_id=call.message.message_id, text=f"Selected: **{skill}**\n\n📥 Requirement likho:", parse_mode="Markdown")

@bot.message_handler(func=lambda message: str(CHAT_ID) in active_work_orders and message.content_type == 'text')
def handle_incoming_requirements(message):
    if str(message.chat.id) != str(CHAT_ID): return
    skill = active_work_orders[str(CHAT_ID)]
    req_text = message.text
    active_work_orders.pop(str(CHAT_ID), None)
    status_msg = bot.reply_to(message, f"⚡ Executing {skill}...")

    final_output = ai_work_executor(skill, req_text)

    if skill in ["YouTube Thumbnail", "Instagram Story"] and "❌" not in final_output:
        img_url = generate_professional_graphic(req_text, skill)
        if img_url:
            bot.send_photo(CHAT_ID, img_url, caption=f"🖼️ Asset Delivered: {skill}")
            bot.delete_message(CHAT_ID, status_msg.message_id)
            return

    conn = sqlite3.connect("agent_ultimate_core.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO completed_works (skill_type, requirement) VALUES (?, ?)", (skill, req_text))
    conn.commit()
    conn.close()

    delivery_payload = f"📦 **Final Deliverable ({skill}):**\n\n{final_output}"
    bot.send_message(CHAT_ID, delivery_payload[:3900], parse_mode="Markdown" if skill != "Web Designing" else None)

    if skill in ["Content Writing", "Script Writing", "Instagram Reels/Shorts"]:
        txt_file, docx_file = create_professional_files(skill, final_output)
        with open(txt_file, "rb") as f:
            bot.send_document(CHAT_ID, f, caption="📄 .txt")
        with open(docx_file, "rb") as f:
            bot.send_document(CHAT_ID, f, caption="💼 .docx")
        if os.path.exists(txt_file): os.remove(txt_file)
        if os.path.exists(docx_file): os.remove(docx_file)

    bot.delete_message(CHAT_ID, status_msg.message_id)

if __name__ == "__main__":
    print("🚀 Booting Up...")
    init_enterprise_db()
    bot.infinity_polling()
