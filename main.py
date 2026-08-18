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
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"users": {}, "redeem_codes": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

bot_data = load_data()

def generate_random_key():
    return f"FF-KEY-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}"

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
        [KeyboardButton("📋 Tasks"), KeyboardButton("🛒 Shop Now")],
        [KeyboardButton("📁 My Keys")]
    ], resize_keyboard=True)

def get_join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{TELEGRAM_CHANNEL.replace('@', '')}")],
        [InlineKeyboardButton("👥 Join Our Group", url=WHATSAPP_GROUP_LINK)],
        [InlineKeyboardButton("✅ জয়েন করেছি, চেক করুন", callback_data="check_join")]
    ])

def get_tasks_menu(u_data):
    tg_text = "✅ Claimed (+30 Pts)" if u_data.get("task_tg_claimed") else "📢 Join Telegram (+30 Pts)"
    wa_text = "✅ Claimed (+30 Pts)" if u_data.get("task_wa_claimed") else "👥 Join WhatsApp (+30 Pts)"
    
    kb = [
        [InlineKeyboardButton(tg_text, callback_data="claim_tg_task")],
        [InlineKeyboardButton(wa_text, callback_data="claim_wa_task")]
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {"name": user.full_name, "points": 0, "keys": [], "referrals": 0, "task_tg_claimed": False, "task_wa_claimed": False}
        save_data(bot_data)
    
    if not await is_member(context.bot, user.id):
        await update.message.reply_text("⚠️ বট ব্যবহারের জন্য আগে জয়েন করুন:", reply_markup=get_join_menu())
    else:
        await update.message.reply_text("✅ স্বাগতম! মেনু থেকে কাজ শুরু করুন।", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    
    if query.data == "check_join":
        if await is_member(context.bot, user_id):
            await query.edit_message_text("✅ স্বাগতম! এখন মেনু দেখুন।", reply_markup=get_main_menu())
        else:
            await query.answer("❌ আপনি এখনো জয়েন করেননি!")
            
    elif query.data == "claim_tg_task":
        if await is_member(context.bot, user_id):
            if not bot_data["users"][user_id].get("task_tg_claimed"):
                bot_data["users"][user_id]["points"] += 30
                bot_data["users"][user_id]["task_tg_claimed"] = True
                save_data(bot_data)
                await query.edit_message_text("🎉 অভিনন্দন! ৩০ পয়েন্ট পেয়েছেন।", reply_markup=get_tasks_menu(bot_data["users"][user_id]))
            else:
                await query.answer("❌ আপনি অলরেডি এটা ক্লেইম করেছেন!")
        else:
            await query.answer("❌ আগে আমাদের চ্যানেলে জয়েন করুন!")
            
    elif query.data == "claim_wa_task":
        # এখানে হোয়াটসঅ্যাপ মেম্বারশিপ চেক করার সরাসরি উপায় নেই, তাই এটি সরাসরি ক্লেইম অপশন হিসেবে কাজ করবে
        if not bot_data["users"][user_id].get("task_wa_claimed"):
            bot_data["users"][user_id]["points"] += 30
            bot_data["users"][user_id]["task_wa_claimed"] = True
            save_data(bot_data)
            await query.edit_message_text("🎉 অভিনন্দন! ৩০ পয়েন্ট পেয়েছেন।", reply_markup=get_tasks_menu(bot_data["users"][user_id]))
        else:
            await query.answer("❌ আপনি অলরেডি এটা ক্লেইম করেছেন!")

    # আপনার আগের কোডের বাকি অংশ (Shop, Buy logic ইত্যাদি) এখানে একইভাবে আছে
    elif query.data == "select_br":
        kb = [[InlineKeyboardButton("1 day - 210 Pts", callback_data="buy_210")], [InlineKeyboardButton("🔙 Back", callback_data="back_to_keys")]]
        await query.edit_message_text("📦 Select a Duration for BR MOD ROOT:", reply_markup=InlineKeyboardMarkup(kb))
    
    elif query.data.startswith("buy_"):
        cost = int(query.data.split("_")[1])
        if bot_data["users"][user_id]["points"] >= cost:
            key = generate_random_key()
            bot_data["users"][user_id]["points"] -= cost
            bot_data["users"][user_id]["keys"].append(key)
            save_data(bot_data)
            await query.edit_message_text(f"✅ সফল! আপনার কী:\n`{key}`", parse_mode="Markdown")
        else:
            await query.answer("❌ Not enough balance!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    if text == "👤 Profile":
        u = bot_data["users"].get(user_id, {})
        await update.message.reply_text(f"👤 নাম: {u.get('name')}\n💎 Balance: {u.get('points')} Points")
    elif text == "📋 Tasks":
        await update.message.reply_text("📋 টাস্ক পূর্ণ করে পয়েন্ট ইনকাম করুন:", reply_markup=get_tasks_menu(bot_data["users"].get(user_id, {})))
    elif text == "🛒 Shop Now":
        await update.message.reply_text("🔗 ভিজিট করুন: https://gofile.io/d/OYS4MC9v")
    elif text == "🔑 Get Key":
        kb = [[InlineKeyboardButton("BR MOD ROOT", callback_data="select_br")]]
        await update.message.reply_text("💎 Select a Product:", reply_markup=InlineKeyboardMarkup(kb))

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.run_polling()
