import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from gpx_processor import process_gpx_file as process_gpx  # <–– подключаем твою функцию

async def gpx_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document.file_name.endswith(".gpx"):
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
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {e}")
        print("Ошибка:", e)

# Запуск бота
app = ApplicationBuilder().token("7704340239:AAFFBXNGHOS2pmZgWeF-2icBieGWMkHsPTg").build()
app.add_handler(MessageHandler(filters.Document.FileExtension("gpx"), gpx_handler))
app.run_polling()
