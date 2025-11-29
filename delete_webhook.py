from aiogram import Bot
import asyncio
import os

async def main():
    bot = Bot(os.getenv("TG_TOKEN"))
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted")

asyncio.run(main())
