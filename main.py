from telegram import Update, Document
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

async def handle_gpx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.file_name.endswith(".gpx"):
        await update.message.reply_text(f"Получен GPX-файл: {file.file_name}")
    else:
        await update.message.reply_text("Пожалуйста, отправь GPX-файл.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_gpx))
    print("🚀 Бот стартует")
    app.run_polling()

if __name__ == "__main__":
    main()
