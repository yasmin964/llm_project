import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Добавьте этот импорт для HTTP сервера
from aiohttp import web
import threading

# Ваш существующий код
from bot.admin_handlers import register_admin_handlers
from bot.user_handlers import register_user_handlers

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения runner
http_runner = None


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


# Добавьте этот код для HTTP сервера
async def health_check(request):
    """Простой endpoint для проверки здоровья"""
    return web.Response(text="Bot is running!")


async def start_http_server():
    """Запускает простой HTTP сервер"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    # Используем порт из переменной окружения или 10000
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"HTTP server started on port {port}")
    return runner


def run_http_server():
    """Запускает HTTP сервер в отдельном event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def setup_server():
        global http_runner
        http_runner = await start_http_server()
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(3600)  # Спим 1 час

    try:
        loop.run_until_complete(setup_server())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


async def main():
    """Запускает бота"""
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
    # Запускаем HTTP сервер в отдельном потоке СНАЧАЛА
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    logger.info("HTTP server starting in background...")

    # Даем время HTTP серверу запуститься
    import time

    time.sleep(3)

    logger.info("Starting Telegram bot...")

    # Запускаем бота в основном потоке
    asyncio.run(main())