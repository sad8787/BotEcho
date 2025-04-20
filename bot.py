#@SadielBotbot:
# Reemplaza esto con tu propio token
TOKEN = "5459892481:AAFdl1xAQKVylQ-1RPjQjJqakNNCBPTroDo"

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("?Hola! Soy un bot de eco. M?ndame un mensaje y lo repetir?.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or ""
    print(message_text)
    await update.message.reply_text(message_text)
    
    

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == '__main__':
    main()

