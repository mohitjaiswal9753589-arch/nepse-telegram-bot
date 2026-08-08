import os
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Bot
from scanner import scan_market

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

NEPAL_TZ = ZoneInfo("Asia/Kathmandu")


def format_message(results):
    if not results:
        return None

    text = "📈 Weekly Fibonacci Scanner\n\n"

    for i, r in enumerate(results, start=1):
        text += (
            f"{i}. {r['symbol']}\n"
            f"Price: {r['price']}\n"
            f"Fib: {r['fib']}\n"
            f"High: {r['high']}\n"
            f"Low: {r['low']}\n"
            f"Distance: {r['percent']}%\n"
            f"Potential: {r['upside']}%\n\n"
        )

    return text


async def run_scanner(bot):
    print("🔎 Scanning market...")

    try:
        results = scan_market()

        print("Total setups found:", len(results))

        if not results:
            print("No setups found.")
            return

        message = format_message(results)

        if message:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=message
            )

            print("✅ Telegram alert sent.")

    except Exception as e:
        print("❌ Scanner Error:", e)


def seconds_until_4_30_pm():
    now = datetime.now(NEPAL_TZ)

    target = now.replace(
        hour=16,
        minute=30,
        second=0,
        microsecond=0
    )

    # If today's 4:30 PM has already passed,
    # schedule tomorrow at 4:30 PM.
    if now >= target:
        target += timedelta(days=1)

    return (target - now).total_seconds()


async def main():
    print("🤖 Bot started")
    print("🇳🇵 Daily scan: 4:30 PM Nepal time")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is missing")
        return

    if not CHAT_ID:
        print("❌ CHAT_ID is missing")
        return

    bot = Bot(token=BOT_TOKEN)

    while True:

        wait_seconds = seconds_until_4_30_pm()

        print(
            f"⏳ Next scan in "
            f"{wait_seconds / 3600:.2f} hours"
        )

        await asyncio.sleep(wait_seconds)

        await run_scanner(bot)

        # Small delay prevents an immediate second run
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
