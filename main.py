from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

async def debug_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Файл получен! Сейчас попробую его обработать.")
    print("✅ Получен файл:", update.message.document.file_name)

app = ApplicationBuilder().token("7704340239:AAFFBXNGHOS2pmZgWeF-2icBieGWMkHsPTg").build()
app.add_handler(MessageHandler(filters.Document.ALL, debug_file_handler))
app.run_polling()
