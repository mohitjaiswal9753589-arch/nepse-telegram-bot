import os
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    try:
        from nepse_data_api import Nepse

        nepse = Nepse()

        message = (
            "📈 NEPSE Scanner Test\n\n"
            + "\n".join(dir(nepse))
        )

    except Exception as e:
        message = (
            "❌ Error\n\n"
            + str(e)
        )

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message[:4000]
    )

if __name__ == "__main__":
    asyncio.run(main())
