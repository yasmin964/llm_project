import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    from bot.telegram_bot import set_webhook_url

    vercel_url = os.getenv("VERCEL_URL")
    if not vercel_url:
        print("ERROR: VERCEL_URL not set in environment")
        vercel_url = input("Enter your Vercel app URL (e.g., https://your-app.vercel.app): ").strip()
        if vercel_url:
            os.environ["VERCEL_URL"] = vercel_url

    success = await set_webhook_url()
    if success:
        print("Webhook set successfully!")
    else:
        print("Failed to set webhook")


if __name__ == "__main__":
    asyncio.run(main())