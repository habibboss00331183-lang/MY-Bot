import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# আপনার টেলিগ্রাম বটের সঠিক টোকেন
TOKEN = "8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ"

# লগিং সেটআপ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# মেমোরিতে ডেটা সংরক্ষণের জন্য ডিকশনারি
user_points = {}
user_referrals = {}
user_data = {}

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    args = context.args
    
    # নতুন ইউজার রেজিস্ট্রেশন
    if user_id not in user_points:
        user_points[user_id] = 0
    if user_id not in user_data:
        user_data[user_id] = {
            "name": user_name,
            "points": 0,
            "keys": [],
            "referrals": 0
        }

    # রেফারেল লজিক
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user_id and referrer_id in user_points:
            user_points[referrer_id] += 10
            user_referrals[referrer_id] = user_referrals.get(referrer_id, 0) + 1
            if referrer_id in user_data:
                user_data[referrer_id]["points"] += 10
                user_data[referrer_id]["referrals"] += 1
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text="🎉 অভিনন্দন! আপনার রেফারেল লিংক থেকে একজন নতুন ইউজার যুক্ত হয়েছে এবং আপনি ১০ পয়েন্ট বোনাস পেয়েছেন!"
                )
            except:
                pass

    # ইনলাইন বাটন বা মেইন মেনু
    keyboard = [
        [InlineKeyboardButton("🔗 Refer & Earn", callback_data="refer"), InlineKeyboardButton("💰 My Points", callback_data="points")],
        [InlineKeyboardButton("🛒 Shop Now", callback_data="buy"), InlineKeyboardButton("📞 Contact Us", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # নিচের ফিক্সড বাটন (Reply Keyboard)
    reply_keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("💰 My Points"), KeyboardButton("🛒 Shop Now")]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    welcome_msg = (
        f"🤖 **Welcome to FF Panel Shop Official Bot!**\n\n"
        f"হ্যালো {user_name}! আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে।"
    )

    await update.message.reply_text(welcome_msg, reply_markup=markup, parse_mode="Markdown")
    await update.message.reply_text("📌 অতিরিক্ত অপশনসমূহ:", reply_markup=reply_markup)

# ইনলাইন বাটন ক্লিক হ্যান্ডলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"name": query.from_user.first_name, "points": 0, "keys": [], "referrals": 0}

    if query.data == "refer":
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        await query.edit_message_text(text=f"🔗 **আপনার রেফারেল লিংক:**\n\n{refer_link}\n\nপ্রতিটি রেফারে পাবেন ১০ পয়েন্ট করে ফ্রি!")
    elif query.data == "points":
        pts = user_data[user_id]["points"]
        refs = user_data[user_id]["referrals"]
        await query.edit_message_text(text=f"💰 **আপনার অ্যাকাউন্ট স্ট্যাটাস:**\n\nপয়েন্ট: {pts}\nমোট রেফার: {refs} জন")
    elif query.data == "buy":
        await query.edit_message_text(text="🛒 শপ মেনু ফাঁকা রয়েছে। শীঘ্রই নতুন আইটেম যুক্ত করা হবে।")
    elif query.data == "contact":
        await query.edit_message_text(text="📞 সাহায্যের জন্য এডমিনের সাথে যোগাযোগ করুন: @Admin")

# সাধারণ টেক্সট মেসেজ হ্যান্ডলার
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.effective_user.id

    if user_id not in user_data:
        user_data[user_id] = {"name": update.effective_user.first_name, "points": 0, "keys": [], "referrals": 0}

    if text == "👤 Profile":
        u_name = user_data[user_id]["name"]
        pts = user_data[user_id]["points"]
        refs = user_data[user_id]["referrals"]
        await update.message.reply_text(f"👤 **প্রফাইল তথ্য:**\n\nনাম: {u_name}\nআইডি: {user_id}\nপয়েন্ট: {pts}\nরেফার: {refs}", parse_mode="Markdown")
    elif text == "🔗 Refer":
        bot_username = context.bot.username
        refer_link = f"https://t.me/{bot_username}?start={user_id}"
        await update.message.reply_text(f"🔗 আপনার রেফারেল লিংক:\n{refer_link}")
    elif text == "💰 My Points":
        pts = user_data[user_id]["points"]
        await update.message.reply_text(f"💰 আপনার বর্তমান পয়েন্ট: {pts}")
    elif text == "🛒 Shop Now":
        await update.message.reply_text("🛒 শপ সেকশনে আপনাকে স্বাগতম।")
    else:
        await update.message.reply_text("দয়া করে নিচের মেনু বাটনগুলো ব্যবহার করুন।")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
