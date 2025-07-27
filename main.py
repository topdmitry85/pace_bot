import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from gpx_processor import process_gpx_file as process_gpx
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

async def gpx_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document or not document.file_name.endswith(".gpx"):
            await update.message.reply_text("📄 Пожалуйста, отправьте GPX-файл.")
            return

        file = await document.get_file()
        local_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(custom_path=local_path)

        await update.message.reply_text("📥 Файл получен! Начинаю анализ...")

        report, image_buffer = process_gpx(local_path)

        if image_buffer:
            await update.message.reply_text(report)
            await update.message.reply_photo(photo=image_buffer, caption="📈 График темпа по дистанции")
        else:
            await update.message.reply_text(report)

        os.remove(local_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {e}")
        print("Ошибка:", e)

# Запуск бота
app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
app.add_handler(MessageHandler(filters.Document.FileExtension("gpx"), gpx_handler))
app.run_polling()
