import logging
import random
import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
SHOP_FILE_LINK = "https://gofile.io/d/OYS4MC9v"
DATA_FILE = "users_data.json"
TELEGRAM_CHANNEL = "@ffpanelshopofficial"

# ডাটা লোড ও সেভ সিস্টেম
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# প্যানেল কী (Keys)
PANEL_KEYS = ["TGR-DRIP-98X7Y-Z65QW", "BRMOD-PASS-43KJH-89LMN", "FF-PANEL-X99V2-B77RT", "SECURE-KEY-88HGF-33DSA"]

# চ্যানেল জয়েন চেক করার ফাংশন
async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=TELEGRAM_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# কি-বোর্ড ডিজাইন
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ], resize_keyboard=True)

def get_join_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ জয়েন করেছি, চেক করুন", callback_data="check_join")]])

# স্টার্ট হ্যান্ডেলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_joined(context.bot, user_id):
        await update.message.reply_text("⚠️ বট ব্যবহারের জন্য আমাদের চ্যানেলে জয়েন করুন:", reply_markup=get_join_keyboard())
    else:
        if str(user_id) not in user_data:
            user_data[str(user_id)] = {"name": update.effective_user.first_name, "points": 0, "keys": [], "referrals": 0}
            save_data(user_data)
        await update.message.reply_text("🤖 স্বাগতম! নিচে মেনু থেকে আপনার প্রয়োজন বেছে নিন।", reply_markup=get_main_keyboard())

# মেসেজ হ্যান্ডেলার
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_joined(context.bot, user_id):
        await update.message.reply_text("⚠️ আগে চ্যানেলে জয়েন করুন!", reply_markup=get_join_keyboard())
        return

    text = update.message.text
    if text == "👤 Profile":
        u = user_data.get(str(user_id), {})
        await update.message.reply_text(f"👤 নাম: {u.get('name')}\n💎 পয়েন্ট: {u.get('points')}\n👥 রেফার: {u.get('referrals')}")
    elif text == "🔗 Refer":
        await update.message.reply_text(f"আপনার রেফারেল লিংক: https://t.me/{context.bot.username}?start={user_id}")
    elif text == "🔑 Get Key":
        await update.message.reply_text("প্রোডাক্ট সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="menu_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT", callback_data="menu_drip")]
        ]))
    elif text == "🛒 Shop Now":
        await update.message.reply_text(f"অফিসিয়াল শপ: {SHOP_FILE_LINK}")
    elif text == "📁 My Keys":
        keys = user_data.get(str(user_id), {}).get("keys", [])
        await update.message.reply_text(f"আপনার কী (Keys): {', '.join(keys) if keys else 'কোনো কী নেই'}")

# বাটন হ্যান্ডেলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_join":
        if await is_joined(context.bot, query.from_user.id):
            await query.edit_message_text("✅ ভেরিফিকেশন সফল! এখন মেনু দেখুন।")
            await context.bot.send_message(query.from_user.id, "🤖 মূল মেনু:", reply_markup=get_main_keyboard())
        else:
            await query.message.reply_text("❌ আপনি এখনো চ্যানেলে জয়েন করেননি!")
    
    elif query.data == "menu_br":
        await query.edit_message_text("BR MOD সিলেক্ট হয়েছে। (পরবর্তী ধাপগুলো এখানে যোগ করুন)")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
