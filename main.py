import logging
import random
import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
SHOP_FILE_LINK = "https://gofile.io/d/OYS4MC9v"
DATA_FILE = "users_data.json"

# আপনার দেওয়া টেলিগ্রাম চ্যানেল এবং হোয়াটসঅ্যাপ চ্যানেলের লিংক
TELEGRAM_CHANNEL_LINK = "https://t.me/ffpanelshopofficial"
WHATSAPP_CHANNEL_LINK = "https://whatsapp.com/channel/0029Vb8ljfP6BIEorl5hXB1T"

# টেলিগ্রাম চ্যানেলের ইউজারনেম (চেক করার জন্য)
REQUIRED_CHANNELS = ["@ffpanelshopofficial"]

# ডেটা লোড ও সেভ করার সিস্টেম (যাতে রেন্ডারে বা অফলাইনে ডেটা মুছে না যায়)
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# প্যানেলের জন্য ৫০টি ইউনিক পাসওয়ার্ড লিস্ট
PANEL_KEYS = [
    "TGR-DRIP-98X7Y-Z65QW-2026", "BRMOD-PASS-43KJH-89LMN-PRO", "FF-PANEL-X99V2-B77RT-VIP",
    "SECURE-KEY-88HGF-33DSA-M1", "ADMIN-TGR-55ABC-77XYZ-PASS", "EXPERT-MOD-12QWE-99POI-LK",
    "LOCKED-KEY-0099V-44BNM-END", "VIP-PANEL-777GH-55JYU-KEY", "CLIENT-MOD-1199A-22BCX-OP",
    "ULTRA-KEY-5544N-33MKO-SYS", "TGR-PRO-111AA-222BB-CC", "BRMOD-VIP-999ZZ-888YY-XX",
    "FF-HACK-55443-22110-PASS", "SECURE-NET-12345-67890-KEY", "ADMIN-BD-98765-43210-SYS",
    "KEY-GEN-11223-33445-PRO", "PANEL-ROOT-55667-77889-VIP", "FREE-FIRE-99001-11223-MOD",
    "DRIP-KEY-44332-22110-SAFE", "TGR-SHOP-77889-99001-PASS", "MOD-BD-12312-34534-PRO",
    "CLIENT-ROOT-98798-65465-KEY", "VIP-USER-11223-44556-SYS", "POWER-KEY-77665-55443-OP",
    "FAST-MOD-33221-11009-VIP", "AUTO-KEY-99887-77665-PRO", "GAME-PASS-55443-33221-SAFE",
    "ROOT-SYS-11223-99887-KEY", "ANDROID-MOD-44556-66778-PASS", "IOS-PANEL-12398-76543-VIP",
    "MAX-KEY-88776-55432-PRO", "ULTRA-MOD-11229-99881-SYS", "EXPERT-KEY-33445-55667-SAFE",
    "MASTER-PANEL-99009-88118-OP", "GHOST-KEY-55667-11223-VIP", "FIRE-MOD-22334-44556-PRO",
    "SPEED-KEY-77889-11223-SYS", "SMOOTH-MOD-33445-66778-PASS", "NO-LAG-99887-44556-VIP",
    "SAFE-KEY-11223-77889-PRO", "CUSTOM-MOD-55667-33445-SAFE", "ONLINE-KEY-99001-22334-SYS",
    "OFFICIAL-PANEL-44556-77889-OP", "TGR-SPECIAL-12345-98765-VIP", "BR-CLIENT-11223-55667-PRO",
    "DRIP-MOD-99887-11223-PASS", "FINAL-KEY-55443-77889-SYS", "TOP-PANEL-33221-99887-VIP",
    "BEST-MOD-11223-44332-PRO", "SECRET-KEY-99009-11223-SAFE"
]

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ইউজার চ্যানেলে জয়েন করেছে কিনা তা চেক করার ফাংশন
async def check_subscription(bot, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

# জয়েন না করলে যে বাটনগুলো দেখাবে
def get_join_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Join Telegram Channel", url=TELEGRAM_CHANNEL_LINK)],
        [InlineKeyboardButton("💬 Join WhatsApp Channel", url=WHATSAPP_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Joined / Verified", callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.first_name
    
    # চ্যানেল সাবস্ক্রিপশন চেক
    is_subscribed = await check_subscription(context.bot, user.id)
    if not is_subscribed:
        await update.message.reply_text(
            "⚠️ Please join our channels first to use this bot.",
            reply_markup=get_join_keyboard()
        )
        return

    args = context.args
    if user_id not in user_data:
        user_data[user_id] = {"name": user_name, "points": 0, "keys": [], "referrals": 0}
        save_data(user_data)

    if args and args[0].isdigit():
        referrer_id = args[0]
        if referrer_id != user_id and referrer_id in user_data:
            user_data[referrer_id]["points"] += 20
            user_data[referrer_id]["referrals"] += 1
            save_data(user_data)
            try:
                await context.bot.send_message(
                    chat_id=int(referrer_id),
                    text="🎁 অভিনন্দন! আপনার রেফারেল লিংক থেকে একজন নতুন ইউজার যুক্ত হয়েছে এবং আপনি ২০ পয়েন্ট বোনাস পেয়েছেন!"
                )
            except:
                pass

    welcome_msg = (
        f"🤖 Welcome to FF Panel Shop Official Bot!\n\n"
        f"👤 User: {user_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"💎 Balance: {user_data[user_id]['points']} Points\n\n"
        f"নিচের মেনু থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন।"
    )

    await update.message.reply_text(welcome_msg, reply_markup=get_main_keyboard())

# টেক্সট মেসেজ হ্যান্ডলার
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text

    is_subscribed = await check_subscription(context.bot, user.id)
    if not is_subscribed:
        await update.message.reply_text(
            "⚠️ Please join our channels first to use this bot.",
            reply_markup=get_join_keyboard()
        )
        return

    if user_id not in user_data:
        user_data[user_id] = {"name": user.first_name, "points": 0, "keys": [], "referrals": 0}
        save_data(user_data)

    if text == "👤 Profile":
        u_data = user_data[user_id]
        profile_text = (
            f"👤 প্রফাইল তথ্য:\n\n"
            f"👤 নাম: {u_data['name']}\n"
            f"🆔 ইউজার আইডি: {user.id}\n"
            f"💎 Balance: {u_data['points']} Points\n"
            f"👥 মোট রেফার: {u_data['referrals']} জন"
        )
        await update.message.reply_text(profile_text)

    elif text == "🔗 Refer":
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={user.id}"
        refer_text = (
            f"🔗 Your Unique Referral Link:\n\n"
            f"{refer_link}\n\n"
            f"👥 Total Referrals: {user_data[user_id]['referrals']} জন\n"
            f"🎁 Earn 20 points for each valid referral."
        )
        await update.message.reply_text(refer_text)

    elif text == "🎟 Redeem Code":
        await update.message.reply_text("🎟 Enter your redeem code.")

    elif text == "🔑 Get Key":
        keyboard = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="menu_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="menu_drip")]
        ]
        await update.message.reply_text("💎 Select a Product:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "🛒 Shop Now":
        keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=SHOP_FILE_LINK)]]
        shop_text = f"🛍 Welcome to our Official Shop!\n\n🔗 Click here: {SHOP_FILE_LINK}"
        await update.message.reply_text(shop_text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "📁 My Keys":
        user_keys = user_data[user_id]["keys"]
        if not user_keys:
            await update.message.reply_text("❌ You have not purchased any keys yet!")
        else:
            keys_list = "\n".join(user_keys)
            await update.message.reply_text(f"🔑 Your Keys:\n\n{keys_list}")

    else:
        await update.message.reply_text("দয়া করে নিচের মেনু বাটনগুলো ব্যবহার করুন।", reply_markup=get_main_keyboard())

# ইনলাইন বাটন হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = str(user.id)
    data = query.data

    if data == "check_join":
        is_subscribed = await check_subscription(context.bot, user.id)
        if is_subscribed:
            if user_id not in user_data:
                user_data[user_id] = {"name": user.first_name, "points": 0, "keys": [], "referrals": 0}
                save_data(user_data)
            await query.message.edit_text("✅ ভেরিফিকেশন সফল হয়েছে! নিচের মেনু ব্যবহার করুন:")
            await context.bot.send_message(chat_id=user.id, text="🤖 মূল মেনু:", reply_markup=get_main_keyboard())
        else:
            await query.answer("❌ আপনি এখনো টেলিগ্রাম চ্যানেলে জয়েন করেননি! দয়া করে জয়েন করুন।", show_alert=True)
        return

    if user_id not in user_data:
        user_data[user_id] = {"name": user.first_name, "points": 0, "keys": [], "referrals": 0}

    if data == "menu_br":
        keyboard = [
            [InlineKeyboardButton("1 days - 210 Pts", callback_data="buy_br_210")],
            [InlineKeyboardButton("7 days - 600 Pts", callback_data="buy_br_600")],
            [InlineKeyboardButton("15 Days - 1000 Pts", callback_data="buy_br_1000")],
            [InlineKeyboardButton("30 Days - 1900 Pts", callback_data="buy_br_1900")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text="💎 Select a Duration:\n\n📦 Product: BR MOD ROOT", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "menu_drip":
        keyboard = [
            [InlineKeyboardButton("1 days - 310 Pts", callback_data="buy_drip_310")],
            [InlineKeyboardButton("7 days - 1210 Pts", callback_data="buy_drip_1210")],
            [InlineKeyboardButton("15 Days - 1890 Pts", callback_data="buy_drip_1890")],
            [InlineKeyboardButton("30 Days - 3690 Pts", callback_data="buy_drip_3690")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text="💎 Select a Duration:\n\n📦 Product: DRIP CLIENT NON ROOT", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="menu_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="menu_drip")]
        ]
        await query.edit_message_text(text="💎 Select a Product:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_"):
        parts = data.split("_")
        product_type = parts[1]
        cost = int(parts[2])
        current_points = user_data[user_id]["points"]
        
        if current_points < cost:
            keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=SHOP_FILE_LINK)]]
            await query.message.reply_text(
                f"❌ Not enough balance! Your current balance is {current_points} Points.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            all_assigned_keys = [k for u in user_data.values() for k in u["keys"]]
            available_keys = [k for k in PANEL_KEYS if k not in all_assigned_keys]
            
            if not available_keys:
                await query.message.reply_text("❌ দুঃখিত, সমস্ত প্যানেল কি (Key) স্টক শেষ হয়ে গেছে!")
                return

            user_data[user_id]["points"] -= cost
            assigned_key = random.choice(available_keys)
            user_data[user_id]["keys"].append(assigned_key)
            save_data(user_data)
            
            p_name = "BR MOD ROOT" if product_type == "br" else "DRIP CLIENT NON ROOT"
            await query.edit_message_text(
                text=f"✅ সফলভাবে আপনার {p_name} কী (Key) জেনারেট হয়েছে!\n\n🔑 পাসওয়ার্ড: {assigned_key}\n\nএটি '📁 My Keys' অপশনে সংরক্ষিত হয়েছে।"
            )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
