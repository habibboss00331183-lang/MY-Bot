import logging
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# আপনার সঠিক টেলিগ্রাম টোকেন এবং শপ লিংক
TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
SHOP_FILE_LINK = "https://gofile.io/d/OYS4MC9v"

# লগিং সেটআপ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ইউজার ডেটা সংরক্ষণের জন্য ডিকশনারি
user_data = {}

# প্যানেলের জন্য ১০টি ইউনিক পাসওয়ার্ড বা কি (Key) লিস্ট
PANEL_KEYS = [
    "TGR-DRIP-98X7Y-Z65QW-2026",
    "BRMOD-PASS-43KJH-89LMN-PRO",
    "FF-PANEL-X99V2-B77RT-VIP",
    "SECURE-KEY-88HGF-33DSA-M1",
    "ADMIN-TGR-55ABC-77XYZ-PASS",
    "EXPERT-MOD-12QWE-99POI-LK",
    "LOCKED-KEY-0099V-44BNM-END",
    "VIP-PANEL-777GH-55JYU-KEY",
    "CLIENT-MOD-1199A-22BCX-OP",
    "ULTRA-KEY-5544N-33MKO-SYS"
]

# ফিক্সড নিচের মেনু বাটন (ইমোজি সহ)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    args = context.args
    
    if user_id not in user_data:
        user_data[user_id] = {
            "name": user_name,
            "points": 5000,  # টেস্ট করার জন্য পর্যাপ্ত পয়েন্ট দেওয়া হলো
            "keys": [],
            "referrals": 0
        }

    # রেফারেল লজিক
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user_id and referrer_id in user_data:
            user_data[referrer_id]["points"] += 200
            user_data[referrer_id]["referrals"] += 1
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎁 Earn 200 points for each valid referral.\n🎉 অভিনন্দন! আপনার রেফারেল লিংক থেকে একজন নতুন ইউজার যুক্ত হয়েছে এবং আপনি ২০০ পয়েন্ট বোনাস পেয়েছেন!"
                )
            except:
                pass

    welcome_msg = (
        f"🤖 **Welcome to FF Panel Shop Official Bot!**\n\n"
        f"👤 User: {user_name}\n"
        f"💎 Balance: {user_data[user_id]['points']} Points\n\n"
        f"নিচের মেনু থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন।"
    )

    await update.message.reply_text(welcome_msg, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# টেক্সট মেসেজ ও বাটন হ্যান্ডলার
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if user_id not in user_data:
        user_data[user_id] = {
            "name": user_name,
            "points": 5000,
            "keys": [],
            "referrals": 0
        }

    if text == "👤 Profile":
        u_data = user_data[user_id]
        profile_text = (
            f"👤 **প্রফাইল তথ্য:**\n\n"
            f"👤 নাম: {u_data['name']}\n"
            f"🆔 ইউজার আইডি: `{user_id}`\n"
            f"💎 Balance: {u_data['points']} Points\n"
            f"👥 মোট রেফার: {u_data['referrals']} জন"
        )
        await update.message.reply_text(profile_text, parse_mode="Markdown")

    elif text == "🔗 Refer":
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        refer_text = (
            f"🔗 **Your Referral Link**\n\n"
            f"`{refer_link}`\n\n"
            f"👥 Total Referrals: {user_data[user_id]['referrals']}\n"
            f"🎁 Earn 200 points for each valid referral."
        )
        await update.message.reply_text(refer_text, parse_mode="Markdown")

    elif text == "🎟 Redeem Code":
        await update.message.reply_text("🎟 Enter your redeem code.")

    elif text == "🔑 Get Key":
        keyboard = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="menu_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="menu_drip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("💎 Select a Product:", reply_markup=reply_markup)

    elif text == "🛒 Shop Now":
        keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=SHOP_FILE_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        shop_text = (
            f"🛍 **Welcome to our Official Shop!**\n\n"
            f"You can buy premium products directly from our website.\n\n"
            f"🔗 Click here: {SHOP_FILE_LINK}"
        )
        await update.message.reply_text(shop_text, reply_markup=reply_markup, parse_mode="Markdown")

    elif text == "📁 My Keys":
        user_keys = user_data[user_id]["keys"]
        if not user_keys:
            await update.message.reply_text("❌ You have not purchased any keys yet!")
        else:
            keys_list = "\n".join(user_keys)
            await update.message.reply_text(f"🔑 **Your Keys:**\n\n{keys_list}", parse_mode="Markdown")

    else:
        await update.message.reply_text("দয়া করে নিচের মেনু বাটনগুলো ব্যবহার করুন।", reply_markup=get_main_keyboard())

# ইনলাইন বাটন ক্লিক হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"name": query.from_user.first_name, "points": 5000, "keys": [], "referrals": 0}

    data = query.data

    # ১. BR MOD ROOT মেনু (পয়েন্ট অপশন)
    if data == "menu_br":
        keyboard = [
            [InlineKeyboardButton("1 days - 210 Pts", callback_data="buy_br_210")],
            [InlineKeyboardButton("7 days - 600 Pts", callback_data="buy_br_600")],
            [InlineKeyboardButton("15 Days - 1000 Pts", callback_data="buy_br_1000")],
            [InlineKeyboardButton("30 Days - 1900 Pts", callback_data="buy_br_1900")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text="💎 Select a Duration:\n\n📦 Product: BR MOD ROOT", reply_markup=InlineKeyboardMarkup(keyboard))

    # ২. DRIP CLIENT NON ROOT মেনু (পয়েন্ট অপশন)
    elif data == "menu_drip":
        keyboard = [
            [InlineKeyboardButton("1 days - 310 Pts", callback_data="buy_drip_310")],
            [InlineKeyboardButton("7 days - 1210 Pts", callback_data="buy_drip_1210")],
            [InlineKeyboardButton("15 Days - 1890 Pts", callback_data="buy_drip_1890")],
            [InlineKeyboardButton("30 Days - 3690 Pts", callback_data="buy_drip_3690")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text="💎 Select a Duration:\n\n📦 Product: DRIP CLIENT NON ROOT", reply_markup=InlineKeyboardMarkup(keyboard))

    # ৩. ব্যাক বাটন
    elif data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="menu_br")],
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="menu_drip")]
        ]
        await query.edit_message_text(text="💎 Select a Product:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ৪. কেনাকাটা এবং পয়েন্ট কাটার লজিক (রেন্ডম পাসওয়ার্ড জেনারেটর)
    elif data.startswith("buy_"):
        parts = data.split("_")
        product_type = parts[1] # br বা drip
        cost = int(parts[2])    # পয়েন্টের পরিমাণ
        
        current_points = user_data[user_id]["points"]
        
        # ব্যালেন্স কম থাকলে শপ লিংকের সাথে এরর দেখাবে
        if current_points < cost:
            keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=SHOP_FILE_LINK)]]
            await query.message.reply_text(
                f"❌ Not enough balance!\n\n🔗 Click here: {SHOP_FILE_LINK}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            user_data[user_id]["points"] -= cost
            assigned_key = random.choice(PANEL_KEYS)
            user_data[user_id]["keys"].append(assigned_key)
            
            p_name = "BR MOD ROOT" if product_type == "br" else "DRIP CLIENT NON ROOT"
            
            await query.edit_message_text(
                text=f"✅ সফলভাবে আপনার **{p_name}** কী (Key) জেনারেট হয়েছে!\n\n🔑 পাসওয়ার্ড: `{assigned_key}`\n\nএটি '📁 My Keys' অপশনে সংরক্ষিত হয়েছে।"
            )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
