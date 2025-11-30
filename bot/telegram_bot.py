import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from flask import Flask
import threading

# Ваш существующий код
from bot.admin_handlers import register_admin_handlers
from bot.user_handlers import register_user_handlers

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Простой Flask сервер
app = Flask(__name__)


@app.route('/')
@app.route('/health')
def health_check():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)


async def start_bot():
    logger.info("Starting Telegram bot...")

    TOKEN = os.getenv("TG_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    register_admin_handlers(dp, ADMIN_ID)
    register_user_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Запускаем бота
    asyncio.run(start_bot())