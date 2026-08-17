from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

# ডামি ডেটাবেস
user_points = {}
user_referrals = {}

# /start কমান্ড হ্যান্ডলার
async def start(update, context):
    user_id = update.effective_user.id
    args = context.args
    
    if user_id not in user_points:
        user_points[user_id] = 0
        
        if args and args[0].isdigit():
            referrer_id = int(args[0])
            if referrer_id != user_id and referrer_id in user_points:
                user_points[referrer_id] += 10
                user_referrals[referrer_id] = user_referrals.get(referrer_id, 0) + 1
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id, 
                        text="🎉 অভিনন্দন! আপনার রেফারেল লিংকে একজন জয়েন করায় ১০ পয়েন্ট যোগ হয়েছে।"
                    )
                except:
                    pass

    # এখানে নতুন রেফারেল ও পয়েন্ট বাটনগুলো যুক্ত করা হলো
    keyboard = [
        [InlineKeyboardButton("🔗 Refer & Earn", callback_data='referral')],
        [InlineKeyboardButton("💰 My Points", callback_data='points')],
        [InlineKeyboardButton("💰 Price List", callback_data='price')],
        [InlineKeyboardButton("📞 Contact Us", callback_data='contact')],
        [InlineKeyboardButton("⚡ Features & Setup", callback_data='features')],
        [InlineKeyboardButton("🛒 How To Buy Panel", callback_data='buy')],
        [InlineKeyboardButton("🟩 Official Rules & Safety", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("স্বাগতম! নিচের অপশনগুলো থেকে বেছে নিন:", reply_markup=reply_markup)

# বাটন ক্লিকে রেসপন্স হ্যান্ডলার
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bot_username = (await context.bot.get_me()).username

    if query.data == 'referral':
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        total_ref = user_referrals.get(user_id, 0)
        await query.message.reply_text(
            f"🔗 **আপনার ব্যক্তিগত রেফারেল লিংক:**\n`{ref_link}`\n\n"
            f"👥 **মোট রেফারেল:** {total_ref} জন\n"
            f"🎁 লিংকের মাধ্যমে কাউকে জয়েন করালে পাবেন ১০ পয়েন্ট!"
        )

    elif query.data == 'points':
        points = user_points.get(user_id, 0)
        await query.message.reply_text(f"💳 **আপনার বর্তমান ব্যালেন্স/পয়েন্ট:** {points} Points")
        
    elif query.data == 'price':
        await query.message.reply_text("💰 আমাদের প্রাইস লিস্ট দেখতে চ্যানেলে ভিজিট করুন।")
    elif query.data == 'contact':
        await query.message.reply_text("📞 যোগাযোগের জন্য আমাদের টেলিগ্রাম ইউজারনেমে মেসেজ দিন।")
    elif query.data == 'features':
        await query.message.reply_text("⚡ প্যানেলের ফিচার এবং সেটআপ সম্পর্কে জানতে গাইড ফলো করুন।")
    elif query.data == 'buy':
        await query.message.reply_text("🛒 প্যানেল কেনার নিয়মাবলী দেখে নিন।")
    elif query.data == 'rules':
        await query.message.reply_text("🟩 অফিসিয়াল রুলস এবং সেফটি মেনে চলুন।")
