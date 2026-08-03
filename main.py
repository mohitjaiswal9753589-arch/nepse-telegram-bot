import os
import asyncio
import inspect
from telegram import Bot
from nepse_data_api import Nepse

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    try:
        nepse = Nepse()

        message = inspect.getdoc(nepse.get_historical_chart)

        if not message:
            message = str(inspect.signature(nepse.get_historical_chart))

    except Exception as e:
        message = str(e)

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message[:4000]
    )

if __name__ == "__main__":
    asyncio.run(main())
