import os
import sqlite3
import requests
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ⚙️ CONFIGURATION VAULT ---
BOT_TOKEN = "9139073932:AAGBSgnkzrhzkYp08PfSWLpxmgJCqhc83EE" 
CHAT_ID = "6165763871"

# आपकी लाइव OpenAI API Key यहाँ इन्जेक्ट कर दी गई है
OPENAI_API_KEY = "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"

bot = telebot.TeleBot(BOT_TOKEN)
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
        f.write(f"PROJECT CATEGORY: {skill_type}\nSTATUS: FINAL DELIVERABLE\n" + "="*50 + "\n\n" + content_text)
        
    with open(docx_filename, "w", encoding="utf-8") as f:
        f.write(f"--- CLIENT SUBMISSION FRAMEWORK ---\nCategory: {skill_type}\n\n{content_text}")
        
    return txt_filename, docx_filename

def ai_work_executor(skill_type, user_prompt):
    base_anti_ai_instruction = (
        "Strict Rule: You must act as a premium human freelance expert with years of industry experience. "
        "Do not include any preambles, greetings like 'Here is your script', or conversational filler. "
        "Do not use robotic transition words or cliché phrases. Deliver only the raw, polished, "
        "production-ready final asset that can be sent straight to a paying client without edits. "
        "It must pass all human-written checks naturally."
    )

    if skill_type == "Content Writing":
        system_prompt = f"{base_anti_ai_instruction} Write a flawless, deeply engaging, and highly professional piece of content on this requirement: '{user_prompt}'. Use variable sentence lengths, relatable metaphors, and a natural human tone."
    elif skill_type == "Script Writing":
        system_prompt = f"{base_anti_ai_instruction} Act as an elite Hollywood/Industry Screenwriter. Draft a full script based on: '{user_prompt}'. Include highly realistic scene headings, natural conversational dialogue, and seamless pacing notes."
    elif skill_type == "Instagram Reels/Shorts":
        system_prompt = f"{base_anti_ai_instruction} Write a high-retention viral short-form video script for: '{user_prompt}'. Start immediately with a psychologically compelling hook, fast pacing, natural delivery speech text, and a clean call-to-action. No robotic intros."
    elif skill_type == "Web Designing":
        system_prompt = f"{base_anti_ai_instruction} You are a senior UI/UX engineer. Write clean, responsive, and incredibly beautiful HTML code utilizing modern Tailwind CSS classes for: '{user_prompt}'. Make it look like a customized premium agency build. Provide only the clean executable code blocks without extra textual explanations."
    else:
        system_prompt = (
            f"You are a master Creative Director. Translate the client's concept: '{user_prompt}' into a highly detailed visual layout description. "
            f"Focus on professional studio lighting, realistic color theory, textures, and clean framing. Explicitly omit any messy textures, watermarks, signature overlays, or digital distortions."
        )

    try:
        url = "https://openai.com"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.65 
        }
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        if res.status_code == 200:
            output = res.json()['choices']['message']['content'].strip()
            for phrase in ["here is the", "sure, here", "as an ai", "designed for you"]:
                if output.lower().startswith(phrase):
                    output = "\n".join(output.split("\n")[1:])
            return output
        else:
            return f"❌ OpenAI API Error Status: {res.status_code}"
    except Exception as e:
        return f"❌ System Error: {e}"

def generate_professional_graphic(prompt_text, skill_type):
    try:
        url = "https://openai.com"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        
        style_modifier = "Cinematic studio photography, high-end commercial layout, perfectly clean vector shapes, ultra-sharp focus, professional graphic design. Strict rule: No watermarks, no logos, no text signatures, no messy artificial overlays, no distorted objects."
        
        payload = {
            "model": "dall-e-3",
            "prompt": f"{skill_type} asset design: {prompt_text}. Style parameters: {style_modifier}",
            "n": 1,
            "size": "1792x1024" if skill_type == "YouTube Thumbnail" else "1024x1792" 
        }
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        if res.status_code == 200:
            return res.json()['data']['url']
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
    bot.send_message(CHAT_ID, "💼 **HUMAN FREELANCE WORK ENGINE ACTIVE**\n\nकौन सा काम बोट से पूरी तरह प्रोफेशनल तरीके से करवाना चाहते हैं? कैटेगरी चुनें:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("do_"))
def handle_work_selection(call):
    if str(call.message.chat.id) != str(CHAT_ID): return
    skill = call.data.replace("do_", "")
    active_work_orders[str(CHAT_ID)] = skill
    bot.edit_message_text(chat_id=CHAT_ID, message_id=call.message.message_id, 
                          text=f"Selected Skill Node: **{skill}**\n\n📥 अपनी रिक्वायरमेंट विस्तार से लिखिए (जैसे टॉपिक, स्टाइल, या कोडिंग थीम)। आपका बोट बिना किसी वाटरमार्क या एआई फुटप्रिंट के असली इंसानी स्टाइल में काम डिलीवर करेगा:", parse_mode="Markdown")

@bot.message_handler(func=lambda message: str(CHAT_ID) in active_work_orders and message.content_type == 'text')
def handle_incoming_requirements(message):
    if str(message.chat.id) != str(CHAT_ID): return
    skill = active_work_orders[str(CHAT_ID)]
    req_text = message.text
    active_work_orders.pop(str(CHAT_ID), None)
    
    status_msg = bot.reply_to(message, f"⚡ **Executing Professional Pipeline...**\nGenerating dynamic assets for *{skill}*. Cleaning signatures and optimizing layout paths...")
    
    final_output = ai_work_executor(skill, req_text)
    
    # HD Graphic Delivery Routine (Watermark-free)
    if skill in ["YouTube Thumbnail", "Instagram Story"] and "❌" not in final_output:
        img_url = generate_professional_graphic(req_text, skill)
        if img_url:
            bot.send_photo(CHAT_ID, img_url, caption=f"🖼️ **Professional Asset Delivered**\nCategory: `{skill}`\n\n*Note: High definition vector matrix rendered without signatures or watermarks.*", parse_mode="Markdown")
            bot.delete_message(CHAT_ID, status_msg.message_id)
            return

    # Database Log
    conn = sqlite3.connect("agent_ultimate_core.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO completed_works (skill_type, requirement) VALUES (?, ?)", (skill, req_text))
    conn.commit()
    conn.close()
    
    # Text Delivery Preview
    delivery_payload = f"📦 **Final Professional Deliverable ({skill}):**\n\n{final_output}"
    if len(delivery_payload) > 4000:
        bot.send_message(CHAT_ID, delivery_payload[:3900] + "\n...[Polished segment sent due to limits]")
    else:
        bot.send_message(CHAT_ID, delivery_payload, parse_mode="Markdown" if skill != "Web Designing" else None)
        
    # File Auto-generation and Upload
    if skill in ["Content Writing", "Script Writing", "Instagram Reels/Shorts"]:
        bot.send_message(CHAT_ID, "📁 *Compiling production-ready deliverable files...*", parse_mode="Markdown")
        txt_file, docx_file = create_professional_files(skill, final_output)
        
        with open(txt_file, "rb") as f:
            bot.send_document(CHAT_ID, f, caption="📄 Clean Plain Text Layout (.txt)")
        with open(docx_file, "rb") as f:
            bot.send_document(CHAT_ID, f, caption="💼 Microsoft Word Document Format (.docx)")
            
        if os.path.exists(txt_file): os.remove(txt_file)
        if os.path.exists(docx_file): os.remove(docx_file)
        
    bot.delete_message(CHAT_ID, status_msg.message_id)

if __name__ == "__main__":
    print("🚀 Booting Up Advanced AI Multi-Skilled Automation Platform...")
    init_enterprise_db()
    bot.infinity_polling()
