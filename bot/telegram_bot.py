import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiohttp import web

from bot.admin_handlers import register_admin_handlers
from bot.user_handlers import register_user_handlers

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


async def health_check(request):
    return web.Response(text="Bot is running!")


async def start_http_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"HTTP server started on port {port}")
    return runner


async def main():
    http_runner = await start_http_server()

    try:
        await start_bot()
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await http_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())