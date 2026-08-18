import random
import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
DATA_FILE = "users_database.json"
TELEGRAM_CHANNEL = "@ffpanelshopofficial"
WHATSAPP_GROUP_LINK = "https://whatsapp.com/channel/0029Vb8ljfP6BIEorl5hXB1T"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: 
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f: 
        json.dump(data, f, indent=4)

bot_data = load_data()

# ৫০টি ইউনিক রেন্ডম কি (Key)
PANEL_KEYS = [f"FF-KEY-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}" for _ in range(50)]

async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=TELEGRAM_CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: 
        return False

def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ], resize_keyboard=True)

def get_join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{TELEGRAM_CHANNEL.replace('@', '')}")],
        [InlineKeyboardButton("👥 Join Our Group", url=WHATSAPP_GROUP_LINK)],
        [InlineKeyboardButton("✅ জয়েন করেছি, চেক করুন", callback_data="check_join")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # রেফারেল বোনাস লজিক (+20 Pts)
    if context.args:
        ref_id = context.args[0]
        if ref_id != user_id and ref_id in bot_data["users"]:
            if user_id not in bot_data["users"]:
                bot_data["users"][ref_id]["points"] += 20
                bot_data["users"][ref_id]["referrals"] += 1
                save_data(bot_data)
                try:
                    await context.bot.send_message(int(ref_id), "🎉 আপনার রেফারেল লিংক দিয়ে একজন নতুন ইউজার জয়েন করেছে! আপনি ২০ পয়েন্ট পেয়েছেন।")
                except:
                    pass

    if not await is_member(context.bot, user.id):
        await update.message.reply_text("⚠️ বট ব্যবহারের জন্য আগে আমাদের চ্যানেল ও হোয়াটসঅ্যাপ গ্রুপে জয়েন করুন:", reply_markup=get_join_menu())
    else:
        if user_id not in bot_data["users"]:
            bot_data["users"][user_id] = {"name": user.first_name, "points": 0, "keys": [], "referrals": 0}
            save_data(bot_data)
        await update.message.reply_text("✅ স্বাগতম! মেনু থেকে কাজ শুরু করুন।", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "check_join":
        if await is_member(context.bot, query.from_user.id):
            if user_id not in bot_data["users"]:
                bot_data["users"][user_id] = {"name": query.from_user.first_name, "points": 0, "keys": [], "referrals": 0}
                save_data(bot_data)
            await query.edit_message_text("✅ ভেরিফিকেশন সফল! এখন বট ব্যবহার করুন।")
            await context.bot.send_message(query.from_user.id, "🤖 মূল মেনু:", reply_markup=get_main_menu())
        else:
            await query.message.reply_text("❌ আপনি এখনো জয়েন করেননি!", reply_markup=get_join_menu())

    elif query.data.startswith("buy_"):
        cost = 210 if query.data == "buy_br" else 310
        if bot_data["users"].get(user_id, {}).get("points", 0) >= cost:
            key = random.choice(PANEL_KEYS)
            bot_data["users"][user_id]["points"] -= cost
            bot_data["users"][user_id]["keys"].append(key)
            save_data(bot_data)
            await query.edit_message_text(f"✅ সফল! আপনার কী হলো:\n`{key}`")
        else:
            await query.answer("❌ পর্যাপ্ত পয়েন্ট নেই!", show_alert=True)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not await is_member(context.bot, update.effective_user.id):
        await update.message.reply_text("⚠️ আগে চ্যানেলে জয়েন করুন!", reply_markup=get_join_menu())
        return

    text = update.message.text
    if text == "👤 Profile":
        u = bot_data["users"].get(user_id, {})
        await update.message.reply_text(f"👤 নাম: {u.get('name')}\n💎 পয়েন্ট: {u.get('points')}\n👥 রেফার: {u.get('referrals')}")
    elif text == "🔗 Refer":
        await update.message.reply_text(f"আপনার রেফার লিংক: https://t.me/{context.bot.username}?start={user_id}")
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
