import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      'হ্যালো হাবিব ভাই! আপনার বটটি সফলভাবে চালু হয়েছে।'
  )


if __name__ == '__main__':
  app = (
      ApplicationBuilder()
      .token('8806345012:AAFxivp7Qnh-dJccphN2Fhf-gIVp5fZs9NQ')
      .build()
  )

  app.add_handler(CommandHandler('start', start))

  app.run_polling()
