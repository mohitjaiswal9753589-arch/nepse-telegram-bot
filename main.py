import os
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://nepse-data-api.vercel.app/api/history"

async def main():

    try:
        response = requests.get(
            API_URL,
            params={"symbol": "NABIL"},
            timeout=10
        )

        data = response.text[:500]

        message = (
            "📊 NEPSE API Test\n\n"
            f"{data}"
        )

    except Exception as e:
        message = f"❌ API Error:\n{e}"

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )


if __name__ == "__main__":
    asyncio.run(main())
