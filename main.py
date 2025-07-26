import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загрузка переменных из .env
load_dotenv()

# Асинхронная функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает!")

# Создание приложения — ВАЖНО: должно идти до add_handler
app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

# Добавляем обработчик команды
app.add_handler(CommandHandler("start", start))

# Лог в Railway
print("🚀 Бот запускается...")

# Запуск
app.run_polling()
