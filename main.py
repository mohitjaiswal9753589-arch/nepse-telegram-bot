import os
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://api.ranjanyadav.com.np/api/nepse/tradingview/history"

def get_weekly_data(symbol):
    params = {
        "symbol": symbol,
        "resolution": "1W"
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    return data


async def main():
    symbol = "NABIL"

    data = get_weekly_data(symbol)

    if "c" in data:
        message = (
            f"📊 NEPSE Data Test\n\n"
            f"Stock: {symbol}\n"
            f"Latest Close: {data['c'][-1]}\n"
            f"Data received ✅"
        )
    else:
        message = f"❌ Data error\n{data}"

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )


if __name__ == "__main__":
    asyncio.run(main())
