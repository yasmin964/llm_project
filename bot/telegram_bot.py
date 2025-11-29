import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from bot.admin_handlers import register_admin_handlers
from bot.user_handlers import register_user_handlers

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting Telegram bot...")

TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logger.info("Creating Bot()...")
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
logger.info("Creating Dispatcher()...")
dp = Dispatcher()
logger.info("Registering handlers...")
# Register all handlers
register_admin_handlers(dp, ADMIN_ID)
register_user_handlers(dp)

logger.info("Starting polling...")
async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
    print("Bot is starting...")