import os, sqlite3, requests, threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG (Safe) ---
BOT_TOKEN = os.getenv("BOT_TOKEN") or "9139073932:AAGBSgnkzrhzkYp08PfSWLpxmgJCqhc83EE"
CHAT_ID = os.getenv("CHAT_ID") or "6165763871"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"

bot = telebot.TeleBot(BOT_TOKEN) if "YOUR_NEW" not in BOT_TOKEN else None
active_work_orders = {}

def init_enterprise_db():
    conn = sqlite3.connect("agent_ultimate_core.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS completed_works (id INTEGER PRIMARY KEY AUTOINCREMENT, skill_type TEXT, requirement TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

def ai_work_executor(skill_type, user_prompt):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        prompt = f"Act as premium human {skill_type} expert. Deliver only final polished asset for: {user_prompt}. No AI footprints."
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.65}
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content'].strip()
        else:
            return f"Error {res.status_code}: Credit khatam hai, $5 add karo"
    except Exception as e:
        return f"Error: {e}"

# --- Telegram Handlers (Same as your code) ---
if bot:
    @bot.message_handler(commands=['dowork'])
    def ask_for_work(message):
        if str(message.chat.id) != str(CHAT_ID): return
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("📝 Content", callback_data="do_Content Writing"), InlineKeyboardButton("📜 Script", callback_data="do_Script Writing"))
        markup.row(InlineKeyboardButton("🌐 Web Design", callback_data="do_Web Designing"), InlineKeyboardButton("🎬 Reels", callback_data="do_Instagram Reels/Shorts"))
        markup.row(InlineKeyboardButton("🖼️ Thumbnail", callback_data="do_YouTube Thumbnail"), InlineKeyboardButton("📸 Story", callback_data="do_Instagram Story"))
        bot.send_message(CHAT_ID, "💼 WORK ENGINE ACTIVE\nCategory chuno:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("do_"))
    def handle_work_selection(call):
        skill = call.data.replace("do_", "")
        active_work_orders[str(CHAT_ID)] = skill
        bot.edit_message_text(chat_id=CHAT_ID, message_id=call.message.message_id, text=f"Selected: {skill}\nRequirement likho:")

    @bot.message_handler(func=lambda message: str(CHAT_ID) in active_work_orders)
    def handle_req(message):
        skill = active_work_orders.pop(str(CHAT_ID))
        final_output = ai_work_executor(skill, message.text)
        bot.send_message(CHAT_ID, f"📦 Final ({skill}):\n\n{final_output[:3500]}")

def start_telegram_bot():
    if bot:
        try:
            bot.infinity_polling()
        except:
            pass

# --- KIVY UI (APK ke liye) ---
class FreelancingUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.add_widget(Label(text='Freelancing OS\nAPK + Telegram Active', size_hint_y=0.2))
        self.status = Label(text='Telegram Bot: Running...\n/dowork bhejo Telegram pe', size_hint_y=0.3)
        self.add_widget(self.status)
        btn = Button(text='Test AI (OpenAI)', size_hint_y=0.2)
        btn.bind(on_press=self.test_ai)
        self.add_widget(btn)
        Clock.schedule_once(lambda dt: threading.Thread(target=start_telegram_bot, daemon=True).start(), 1)

    def test_ai(self, instance):
        self.status.text = ai_work_executor("Content Writing", "Test content")[:500]

class MyApp(App):
    def build(self):
        init_enterprise_db()
        return FreelancingUI()

MyApp().run()
