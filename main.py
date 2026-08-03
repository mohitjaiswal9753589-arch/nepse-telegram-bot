import os
import asyncio
from telegram import Bot
from nepse_data_api import Nepse

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    try:
        nepse = Nepse()

        data = nepse.get_historical_chart("NABIL")

        message = (
            "📈 Historical Chart Test\n\n"
            + str(data)[:3500]
        )

    except Exception as e:
        message = (
            "❌ Error\n\n"
            + str(e)
        )

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

if __name__ == "__main__":
    asyncio.run(main())
