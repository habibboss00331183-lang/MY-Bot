import random
import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- কনফিগারেশন ---
TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
DATA_FILE = "users_database.json"
CHANNEL_LINK = "@ffpanelshopofficial"
GROUP_LINK = "@your_group_username" 

# --- লগিং সিস্টেম (বট কেন কাজ করছে না তা দেখার জন্য) ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ৫০টি রেন্ডম কি (Keys) জেনারেটর ---
def generate_keys():
    return [f"KEY-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}" for _ in range(50)]

PANEL_KEYS = generate_keys()

# --- ডাটাবেস হ্যান্ডলিং ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

bot_data = load_data()

# --- জয়েনিং চেক লজিক ---
async def is_member(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# --- মেনু বাটনস ---
def get_main_menu():
    keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_join_menu():
    keyboard = [
        [InlineKeyboardButton("📢 চ্যানেল জয়েন করুন", url=f"https://t.me/{CHANNEL_LINK.replace('@', '')}")],
        [InlineKeyboardButton("👥 গ্রুপ জয়েন করুন", url=f"https://t.me/{GROUP_LINK.replace('@', '')}")],
        [InlineKeyboardButton("✅ জয়েন করেছি, চেক করুন", callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- মেইন হ্যান্ডেলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    # রেফারেল লজিক
    if context.args:
        ref_id = context.args[0]
        if ref_id != user_id and ref_id in bot_data["users"]:
            if user_id not in bot_data["users"]:
                bot_data["users"][ref_id]["points"] += 20
                bot_data["users"][ref_id]["referrals"] += 1
                save_data(bot_data)
                try:
                    await context.bot.send_message(int(ref_id), "🎉 নতুন রেফারেল থেকে ২০ পয়েন্ট পেয়েছেন!")
                except: pass

    # চ্যানেল-গ্রুপ জয়েন চেক
    if not await is_member(context.bot, user.id, CHANNEL_LINK) or not await is_member(context.bot, user.id, GROUP_LINK):
        await update.message.reply_text("⚠️ **বট ব্যবহারের জন্য আগে চ্যানেল এবং গ্রুপে জয়েন করুন!**", reply_markup=get_join_menu())
    else:
        if user_id not in bot_data["users"]:
            bot_data["users"][user_id] = {"name": user.first_name, "points": 0, "keys": [], "referrals": 0}
            save_data(bot_data)
        await update.message.reply_text("✅ স্বাগতম! মেনু থেকে কাজ শুরু করুন।", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()

    if query.data == "check_join":
        if await is_member(context.bot, query.from_user.id, CHANNEL_LINK) and await is_member(context.bot, query.from_user.id, GROUP_LINK):
            if user_id not in bot_data["users"]:
                bot_data["users"][user_id] = {"name": query.from_user.first_name, "points": 0, "keys": [], "referrals": 0}
                save_data(bot_data)
            await query.edit_message_text("✅ ভেরিফিকেশন সফল! এখন বট ব্যবহার করুন।")
            await context.bot.send_message(query.from_user.id, "🤖 মূল মেনু:", reply_markup=get_main_menu())
        else:
            await query.message.reply_text("❌ আপনি এখনো সব জায়গায় জয়েন করেননি!", reply_markup=get_join_menu())

    elif query.data.startswith("buy_"):
        cost = 210 if query.data == "buy_br" else 310
        if bot_data["users"][user_id]["points"] >= cost:
            key = random.choice(PANEL_KEYS)
            bot_data["users"][user_id]["points"] -= cost
            bot_data["users"][user_id]["keys"].append(key)
            save_data(bot_data)
            await query.edit_message_text(f"✅ সফল! আপনার কী: `{key}`")
        else:
            await query.answer("❌ পর্যাপ্ত পয়েন্ট নেই!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # প্রতি মেসেজে জয়েনিং চেক
    if not await is_member(context.bot, update.effective_user.id, CHANNEL_LINK) or not await is_member(context.bot, update.effective_user.id, GROUP_LINK):
        await update.message.reply_text("⚠️ আগে জয়েন করুন!", reply_markup=get_join_menu())
        return

    text = update.message.text
    if text == "👤 Profile":
        u = bot_data["users"].get(user_id, {})
        await update.message.reply_text(f"👤 নাম: {u.get('name')}\n💎 পয়েন্ট: {u.get('points')}\n👥 রেফার: {u.get('referrals')}")
    elif text == "🔗 Refer":
        await update.message.reply_text(f"লিংক: https://t.me/{context.bot.username}?start={user_id}")
    elif text == "🔑 Get Key":
        kb = [[InlineKeyboardButton("📦 BR MOD (210 Pts)", callback_data="buy_br")],
              [InlineKeyboardButton("📦 DRIP CLIENT (310 Pts)", callback_data="buy_drip")]]
        await update.message.reply_text("💎 সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(kb))
    elif text == "📁 My Keys":
        keys = bot_data["users"].get(user_id, {}).get("keys", [])
        await update.message.reply_text(f"আপনার কী:\n{', '.join(keys) if keys else 'কোনো কী নেই'}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
