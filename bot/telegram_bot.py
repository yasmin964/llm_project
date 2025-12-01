import os
import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from aiohttp import web

from bot.admin_handlers import register_admin_handlers
from bot.user_handlers import register_user_handlers
from rag.config import DOCS_DIR

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_instance = None
dp_instance = None


async def setup_bot():
    global bot_instance, dp_instance

    if bot_instance is not None:
        return bot_instance, dp_instance

    logger.info("Setting up Telegram bot...")

    TOKEN = os.getenv("TG_TOKEN")
    if not TOKEN:
        raise ValueError("TG_TOKEN not found in environment variables")

    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

    bot_instance = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp_instance = Dispatcher()

    register_admin_handlers(dp_instance, ADMIN_ID)
    register_user_handlers(dp_instance)

    logger.info("Bot setup completed")
    return bot_instance, dp_instance


async def process_webhook_update(update_data: dict):
    try:
        bot, dp = await setup_bot()

        update = Update(**update_data)

        await dp.feed_webhook_update(bot, update)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {"status": "error", "message": str(e)}


async def handle_webhook(request: web.Request):
    try:
        data = await request.json()

        response = await process_webhook_update(data)

        return web.json_response(response)

    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        return web.Response(status=400, text="Invalid JSON")
    except Exception as e:
        logger.error(f"Error in handle_webhook: {e}")
        return web.Response(status=500, text=str(e))


async def health_check(request):
    return web.Response(text="Bot webhook server is running!")


async def start_polling():
    bot, dp = await setup_bot()

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Starting bot in polling mode...")
    await dp.start_polling(bot)


async def set_webhook_url():
    bot, _ = await setup_bot()

    vercel_url = os.getenv("VERCEL_URL")
    if not vercel_url:
        vercel_url = os.getenv("WEBHOOK_URL", "")

    if vercel_url:
        webhook_url = f"{vercel_url}/api/bot"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True

    return False


async def start_local_webhook_server():
    app = web.Application()

    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    app.router.add_post('/api/bot', handle_webhook)

    await setup_bot()

    port = int(os.environ.get('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)

    logger.info(f"Local webhook server started on port {port}")
    logger.info("Use ngrok to expose: ngrok http 8080")

    return runner, site


if __name__ == "__main__":
    use_webhook = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    local_server = os.getenv("LOCAL_SERVER", "false").lower() == "true"

    if local_server:
        print("Starting local webhook server...")
        print("Use with ngrok for testing:")
        print("ngrok http 8080")


        async def main_local():
            runner, site = await start_local_webhook_server()
            await site.start()

            try:
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                print("\nShutting down...")
                await runner.cleanup()


        asyncio.run(main_local())

    elif use_webhook:
        print("Setting up webhook for Vercel...")


        async def main_set_webhook():
            success = await set_webhook_url()
            if success:
                print("Webhook set successfully!")
                print("Bot is running on Vercel with webhook")
            else:
                print("Failed to set webhook")
                print("Please set VERCEL_URL environment variable")


        asyncio.run(main_set_webhook())

    else:
        print("Starting bot in polling mode (for development)...")
        asyncio.run(start_polling())