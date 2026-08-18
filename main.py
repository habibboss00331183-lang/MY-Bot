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
        except Exception:
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
    except Exception:
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
    tg_status = "✅ Done (+30 Pts)" if u_data.get("task_tg_claimed") else "📢 Join Telegram (+30 Pts)"
    wa_status = "✅ Done (+30 Pts)" if u_data.get("task_wa_claimed") else "👥 Join WhatsApp (+30 Pts)"
    
    kb = []
    if not u_data.get("task_tg_claimed"):
        kb.append([InlineKeyboardButton(tg_status, callback_data="claim_tg_task")])
    else:
        kb.append([InlineKeyboardButton(tg_status, callback_data="already_claimed")])
        
    if not u_data.get("task_wa_claimed"):
        kb.append([InlineKeyboardButton(wa_status, callback_data="claim_wa_task")])
    else:
        kb.append([InlineKeyboardButton(wa_status, callback_data="already_claimed")])
        
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.full_name if user.full_name else user.first_name

    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "name": user_name,
            "points": 0,
            "keys": [],
            "referrals": 0,
            "task_tg_claimed": False,
            "task_wa_claimed": False
        }
        save_data(bot_data)
    else:
        bot_data["users"][user_id]["name"] = user_name
        save_data(bot_data)

    if context.args:
        ref_id = context.args[0]
        if ref_id != user_id and ref_id in bot_data["users"]:
            if "referred_by" not in bot_data["users"][user_id]:
                bot_data["users"][user_id]["referred_by"] = ref_id
                bot_data["users"][ref_id]["points"] += 20
                bot_data["users"][ref_id]["referrals"] += 1
                save_data(bot_data)
                try:
                    await context.bot.send_message(int(ref_id), "🎉 আপনার রেফারেল লিংক দিয়ে একজন নতুন ইউজার জয়েন করেছে! আপনি ২০ পয়েন্ট পেয়েছেন।")
                except Exception:
                    pass

    if not await is_member(context.bot, user.id):
        await update.message.reply_text("⚠️ বট ব্যবহারের জন্য আগে আমাদের চ্যানেল ও হোয়াটসঅ্যাপ গ্রুপে জয়েন করুন:", reply_markup=get_join_menu())
    else:
        await update.message.reply_text("✅ স্বাগতম! মেনু থেকে কাজ শুরু করুন।", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "name": query.from_user.full_name,
            "points": 0,
            "keys": [],
            "referrals": 0,
            "task_tg_claimed": False,
            "task_wa_claimed": False
        }
        save_data(bot_data)

    if query.data == "check_join":
        if await is_member(context.bot, query.from_user.id):
            await query.edit_message_text("✅ ভেরিফিকেশন সফল!")
            await context.bot.send_message(query.from_user.id, "✅ স্বাগতম! মেনু থেকে কাজ শুরু করুন।", reply_markup=get_main_menu())
        else:
            await query.message.reply_text("❌ আপনি এখনো জয়েন করেননি!", reply_markup=get_join_menu())

    elif query.data == "claim_tg_task":
        if await is_member(context.bot, query.from_user.id):
            if not bot_data["users"][user_id].get("task_tg_claimed", False):
                bot_data["users"][user_id]["points"] += 30
                bot_data["users"][user_id]["task_tg_claimed"] = True
                save_data(bot_data)
                await query.edit_message_text("🎉 অভিনন্দন! টেলিগ্রাম চ্যানেলে জয়েন করার জন্য আপনি ৩০ পয়েন্ট পেয়েছেন।", reply_markup=get_tasks_menu(bot_data["users"][user_id]))
            else:
                await query.message.reply_text("❌ আপনি ইতিমধ্যে এই টাস্কটির পয়েন্ট পেয়ে গেছেন!")
        else:
            await query.message.reply_text("❌ আগে টেলিগ্রাম চ্যানেলে জয়েন করুন!", reply_markup=get_join_menu())

    elif query.data == "claim_wa_task":
        if not bot_data["users"][user_id].get("task_wa_claimed", False):
            bot_data["users"][user_id]["points"] += 30
            bot_data["users"][user_id]["task_wa_claimed"] = True
            save_data(bot_data)
            await query.edit_message_text("🎉 অভিনন্দন! হোয়াটসঅ্যাপ চ্যানেলে জয়েন করার জন্য আপনি ৩০ পয়েন্ট পেয়েছেন।", reply_markup=get_tasks_menu(bot_data["users"][user_id]))
        else:
            await query.message.reply_text("❌ আপনি ইতিমধ্যে এই টাস্কটির পয়েন্ট পেয়ে গেছেন!")

    elif query.data == "already_claimed":
        await query.message.reply_text("✅ এই টাস্কটির পয়েন্ট আপনি আগেই ক্লেইম করেছেন।")

    elif query.data == "select_br":
        kb = [
            [InlineKeyboardButton("1 days - 210 Pts", callback_data="buy_210")],
            [InlineKeyboardButton("7 days - 600 Pts", callback_data="buy_600")],
            [InlineKeyboardButton("15 Days - 1000 Pts", callback_data="buy_1000")],
            [InlineKeyboardButton("30 Days - 1900 Pts", callback_data="buy_1900")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_keys")]
        ]
        await query.edit_message_text("💎 Select a Duration:\n\n📦 Product: BR MOD ROOT", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "select_drip":
        kb = [
            [InlineKeyboardButton("1 days - 310 Pts", callback_data="buy_310")],
            [InlineKeyboardButton("7 days - 750 Pts", callback_data="buy_750")],
            [InlineKeyboardButton("15 Days - 1200 Pts", callback_data="buy_1200")],
            [InlineKeyboardButton("30 Days - 2200 Pts", callback_data="buy_2200")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_keys")]
        ]
        await query.edit_message_text("💎 Select a Duration:\n\n📦 Product: DRIP CLIENT NON ROOT", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "back_to_keys":
        kb = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="select_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="select_drip")]
        ]
        await query.edit_message_text("💎 Select a Product:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("buy_"):
        cost = int(query.data.split("_")[1])
        user_points = bot_data["users"].get(user_id, {}).get("points", 0)
        
        if user_points >= cost:
            key = generate_random_key()
            bot_data["users"][user_id]["points"] -= cost
            bot_data["users"][user_id]["keys"].append(key)
            save_data(bot_data)
            await query.edit_message_text(f"✅ সফল! আপনার কী:\n`{key}`", parse_mode="Markdown")
        else:
            await query.message.reply_text(f"❌ Not enough balance! Your current balance is {user_points} Points.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.full_name if user.full_name else user.first_name

    if user_id not in bot_data["users"]:
        bot_data["users"][user_id] = {
            "name": user_name,
            "points": 0,
            "keys": [],
            "referrals": 0,
            "task_tg_claimed": False,
            "task_wa_claimed": False
        }
        save_data(bot_data)

    if not await is_member(context.bot, user.id):
        await update.message.reply_text("⚠️ বট ব্যবহারের জন্য আগে আমাদের চ্যানেল ও হোয়াটসঅ্যাপ গ্রুপে জয়েন করুন:", reply_markup=get_join_menu())
        return

    text = update.message.text

    if text == "👤 Profile":
        u = bot_data["users"].get(user_id, {})
        msg = f"👤 প্রফাইল তথ্য:\n\n👤 নাম: {u.get('name')}\n🆔 ইউজার আইডি: {user_id}\n💎 Balance: {u.get('points')} Points\n👥 মোট রেফার: {u.get('referrals')} জন"
        await update.message.reply_text(msg)

    elif text == "🔗 Refer":
        u = bot_data["users"].get(user_id, {})
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        msg = f"🔗 Your Unique Referral Link:\n\n{referral_link}\n\n👥 Total Referrals: {u.get('referrals')} জন\n🎁 Earn 20 points for each valid referral."
        await update.message.reply_text(msg)

    elif text == "📋 Tasks":
        u = bot_data["users"].get(user_id, {})
        await update.message.reply_text("📋 নিচের চ্যানেলগুলোতে জয়েন করে পয়েন্ট ক্লেইম করুন (প্রতিটি ৩০ পয়েন্ট):", reply_markup=get_tasks_menu(u))

    elif text == "🔑 Get Key":
        kb = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="select_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="select_drip")]
        ]
        await update.message.reply_text("💎 Select a Product:", reply_markup=InlineKeyboardMarkup(kb))

    elif text == "📁 My Keys":
        keys = bot_data["users"].get(user_id, {}).get("keys", [])
        if keys:
            keys_formatted = "\n".join([f"`{k}`" for k in keys])
            await update.message.reply_text(f"🔑 আপনার কেনা কী সমূহ:\n\n{keys_formatted}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ You have not purchased any keys yet!")

    elif text == "🛒 Shop Now":
        kb = [[InlineKeyboardButton("🌐 Open Shop Website", url="https://gofile.io/d/OYS4MC9v")]]
        await update.message.reply_text("🛍️ Welcome to our Official Shop!\n\n🔗 Click here: https://gofile.io/d/OYS4MC9v", reply_markup=InlineKeyboardMarkup(kb))

    elif text == "🎟 Redeem Code":
        await update.message.reply_text("🎟️ Enter your redeem code.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
