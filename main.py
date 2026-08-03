import os
import asyncio
from telegram import Bot
from nepse_data_api import Nepse

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def main():
    try:
        nepse = Nepse()

        securities = nepse.get_security_list()

        message = str(securities)[:4000]

    except Exception as e:
        message = str(e)

    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(main())
