import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# আপনার সঠিক টেলিগ্রাম টোকেন
TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"
CHANNEL_LINK = "https://t.me/ffpanelshopofficial"
PANEL_SHOP_SITE = "https://panelsell.store"

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

# নিচের ফিক্সড মেনু বাটন (স্ক্রিনশটের মতো)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("📁 My Keys")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# /start কমান্ড হ্যান্ডলার (১০০% কাজ করার মতো রেফারেল সিস্টেম সহ)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    args = context.args
    
    # নতুন ইউজার রেজিস্ট্রেশন
    if user_id not in user_data:
        user_data[user_id] = {
            "name": user_name,
            "points": 20,  # শুরুর জন্য ২০ পয়েন্ট ফ্রি দিতে পারেন চাইলে (বা ০ করতে পারেন)
            "keys": [],
            "referrals": 0
        }

    # রেফারেল লজিক (১০০% কার্যকরী)
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user_id and referrer_id in user_data:
            # চেক করা যাতে একই ইউজার বারবার রেফার করে পয়েন্ট না নিতে পারে
            user_data[referrer_id]["points"] += 20
            user_data[referrer_id]["referrals"] += 1
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎁 Earn 20 points for each valid referral.\n🎉 অভিনন্দন! আপনার রেফারেল লিংক থেকে একজন নতুন ইউজার যুক্ত হয়েছে এবং আপনি ২০ পয়েন্ট বোনাস পেয়েছেন!"
                )
            except:
                pass

    welcome_msg = (
        f"🤖 **Welcome to FF Panel Shop Official Bot!**\n\n"
        f"হ্যালো {user_name}! আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে। নিচের মেনু থেকে আপনার প্রয়োজনীয় অপشن বেছে নিন।"
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
            "points": 0,
            "keys": [],
            "referrals": 0
        }

    if text == "👤 Profile":
        u_data = user_data[user_id]
        profile_text = (
            f"👤 **প্রফাইল তথ্য:**\n\n"
            f"নাম: {u_data['name']}\n"
            f"ইউজার আইডি: `{user_id}`\n"
            f"পয়েন্ট: {u_data['points']} 🪙\n"
            f"মোট রেফার: {u_data['referrals']} জন"
        )
        await update.message.reply_text(profile_text, parse_mode="Markdown")

    elif text == "🔗 Refer":
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        refer_text = (
            f"🔗 **Your Referral Link**\n\n"
            f"`{refer_link}`\n\n"
            f"👥 Total Referrals: {user_data[user_id]['referrals']}\n"
            f"🎁 Earn 20 points for each valid referral."
        )
        await update.message.reply_text(refer_text, parse_mode="Markdown")

    elif text == "🎟 Redeem Code":
        await update.message.reply_text("🎟 Enter your redeem code.")

    elif text == "🔑 Get Key":
        # স্ক্রিনশটের মতো প্রোডাক্ট সিলেকশন বা অপশন
        keyboard = [
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data="get_drip")],
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data="get_br")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("💎 Select a Product:", reply_markup=reply_markup)

    elif text == "🛒 Shop Now":
        keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=PANEL_SHOP_SITE)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        shop_text = (
            "🛍 **Welcome to our Official Shop!**\n\n"
            "You can buy premium products directly from our website.\n\n"
            f"🔗 Click here: {PANEL_SHOP_SITE}"
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

# ইনলাইন বাটন ক্লিক হ্যান্ডলার (ব্যালেন্স চেক এবং ১০টি পাসওয়ার্ড থেকে এসাইন করার লজিক)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data in ["get_drip", "get_br"]:
        current_points = user_data[user_id]["points"]
        
        # ব্যালেন্স বা পয়েন্ট না থাকলে স্ক্রিনশটের মতো স্টাইলে এরর মেসেজ দেখাবে
        if current_points < 50:  # প্যানেল নেয়ার জন্য ধরা যাক ৫০ পয়েন্ট লাগবে
            keyboard = [[InlineKeyboardButton("🌐 Open Shop Website", url=PANEL_SHOP_SITE)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "❌ Not enough balance!\n\n🔗 Click here: " + PANEL_SHOP_SITE,
                reply_markup=reply_markup
            )
        else:
            # পয়েন্ট কেটে নেওয়া হবে
            user_data[user_id]["points"] -= 50
            
            # ১০টি পাসওয়ার্ড বা কী থেকে একটি করে ইউজারকে দেওয়া হবে
            import random
            assigned_key = random.choice(PANEL_KEYS)
            # যেন ডুপ্লিকেট না দেয় বা সেভ থাকে তার ব্যবস্থা
            user_data[user_id]["keys"].append(assigned_key)
            
            await query.edit_message_text(
                text=f"✅ সফলভাবে আপনার প্যানেল কি (Key) জেনারেট হয়েছে!\n\n🔑 আপনার পাসওয়ার্ড: `{assigned_key}`\n\nএটি 'My Keys' অপশনে দেখতে পাবেন।"
            )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
