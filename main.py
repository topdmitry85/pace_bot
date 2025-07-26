import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from gpx_processor import process_gpx_file as process_gpx

from telegram.ext import CommandHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Бот запущен и работает!")

app.add_handler(CommandHandler("start", start))


async def gpx_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document or not document.file_name.endswith(".gpx"):
            await update.message.reply_text("Пожалуйста, отправьте GPX-файл.")
            return

        file = await document.get_file()
        local_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(custom_path=local_path)

        await update.message.reply_text("📥 Файл получен! Начинаю анализ...")

        result = process_gpx(local_path)

        await update.message.reply_text(result)

        os.remove(local_path)

    except Exception as e:
        await update.message.reply_text("❌ Ошибка при обработке файла.")
        print("Ошибка:", e)

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(MessageHandler(filters.Document.FileExtension("gpx"), gpx_handler))
    app.run_polling()
