import os
import asyncio
from telegram import Bot
from scanner import scan_market

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


        
def format_message(results):
    if not results:
        print("Total setups found:", len(results))
        print("Results:", results)
        return "📉 Weekly Scanner\n\nNo setups found."

    text = "📈 Weekly Fibonacci Scanner\n\n"

    for i, r in enumerate(results, start=1):
        text += (
            f"{i}. {r['symbol']}\n"
            f"Price : {r['price']}\n"
            f"Fib : {r['fib']}\n"
            f"High : {round(r['high'], 2)}\n"
            f"Low : {round(r['low'], 2)}\n"
            f"Distance : {r['percent']}%\n"
            f"Potential : {r['upside']}%\n\n"
        )

    return text


async def main():
    print("Bot started")

    bot = Bot(token=BOT_TOKEN)

    try:

        results = scan_market(nepse)

        message = format_message(results)

    except Exception as e:
        message = (
            "❌ Scanner Error\n\n"
            + str(e)
        )

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

    except Exception as e:
        print(f"Telegram Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    
    
