import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# আপনার টেলিগ্রাম বটের টোকেন এখানে বসানো আছে
TOKEN = "7961226749:AAEMf06xUj1V63r84Ff8d1Z6K97f4kX7x-g"

# ডামি ডেটাবেস
user_data = {}

# /start কমান্ড ও নিচের রিপ্লাই কিবোর্ড (Persistent Menu)
async def start(update, context):
    user = update.effective_user
    user_id = user.id
    args = context.args
    
    if user_id not in user_data:
        user_data[user_id] = {
            "name": user.full_name,
            "points": 0,
            "keys": [],
            "referrals": 0
        }
        
        # রেফারেল লজিক
        if args and args[0].isdigit():
            referrer_id = int(args[0])
            if referrer_id != user_id and referrer_id in user_data:
                user_data[referrer_id]["points"] += 20
                user_data[referrer_id]["referrals"] += 1
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id, 
                        text="🎉 অভিনন্দন! আপনার রেফারেল লিংকে একজন জয়েন করায় ২০ পয়েন্ট যোগ হয়েছে।"
                    )
                except:
                    pass

    # স্ক্রিনশটের নিচের দিকের মেনু বাটনগুলো (Reply Keyboard)
    reply_keyboard = [
        [KeyboardButton("👤 Profile"), KeyboardButton("🔗 Refer")],
        [KeyboardButton("🎟 Redeem Code"), KeyboardButton("🔑 Get Key")],
        [KeyboardButton("🛒 Shop Now"), KeyboardButton("🔑 My Keys")]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ Verification successful.\n\nস্বাগতম {user.first_name}!\nনিচের মেনু থেকে আপনার প্রয়োজনীয় অপশনটি বেছে নিন:",
        reply_markup=markup
    )

# নিচের মেনু বাটনের টেক্সট হ্যান্ডলার
async def message_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    user = update.effective_user
    bot_username = (await context.bot.get_me()).username

    if user_id not in user_data:
        user_data[user_id] = {"name": user.full_name, "points": 0, "keys": [], "referrals": 0}

    if text == "👤 Profile":
        data = user_data[user_id]
        profile_text = (
            f"👤 **User Profile**\n\n"
            f"📌 **Name:** {user.full_name}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"💰 **Points / Tokens:** {data['points']} Points\n"
            f"👥 **Total Referrals:** {data['referrals']} জন"
        )
        await update.message.reply_text(profile_text, parse_mode="Markdown")

    elif text == "🔗 Refer":
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        total_ref = user_data[user_id]["referrals"]
        await update.message.reply_text(
            f"🔗 **Your Referral Link**\n`{ref_link}`\n\n"
            f"👥 **Total Referrals:** {total_ref}\n"
            f"🎁 Earn 20 points for each valid referral."
        )

    elif text == "🎟 Redeem Code":
        await update.message.reply_text("❌ Invalid redeem code.")

    elif text == "🔑 Get Key":
        await update.message.reply_text("🔑 আপনার জেনারেট করা ফ্রি কি (Key) পেতে চ্যানেলে যুক্ত থাকুন।")

    elif text == "🛒 Shop Now":
        # প্রোডাক্ট বা ইনলাইন শপ মেনু
        keyboard = [
            [InlineKeyboardButton("📦 DRIP CLIENT NON ROOT", callback_data='p1')],
            [InlineKeyboardButton("📦 BR MOD ROOT", callback_data='p2')],
            [InlineKeyboardButton("📦 ANGRY MOD", callback_data='p3')],
            [InlineKeyboardButton("📦 PRIME MOD", callback_data='p4')],
            [InlineKeyboardButton("📦 HG CHEAT", callback_data='p5')],
            [InlineKeyboardButton("📦 zytron Pro Internal", callback_data='p6')],
            [InlineKeyboardButton("📦 Anonymous Pro", callback_data='p7')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🛒 **Select a Product:**", reply_markup=reply_markup)

    elif text == "🔑 My Keys":
        keys = user_data[user_id]["keys"]
        if keys:
            keys_list = "\n".join(keys)
            await update.message.reply_text(f"🔑 **Your Active Keys:**\n{keys_list}")
        else:
            await update.message.reply_text("🔑 আপনার কোনোভল অ্যাক্টিভ কি (Key) নেই।")

# শপ বাটনের ইনলাইন ক্লিক হ্যান্ডলার
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    products = {
        'p1': 'DRIP CLIENT NON ROOT',
        'p2': 'BR MOD ROOT',
        'p3': 'ANGRY MOD',
        'p4': 'PRIME MOD',
        'p5': 'HG CHEAT',
        'p6': 'zytron Pro Internal',
        'p7': 'Anonymous Pro'
    }
    
    prod_name = products.get(query.data, 'Product')
    await query.message.reply_text(f"🛒 আপনি সিলেক্ট করেছেন: **{prod_name}**\nপেমেন্ট বা কেনার বিস্তারিত জানতে এডমিনের সাথে যোগাযোগ করুন।")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == '__main__':
    main()
