import os
import asyncio
import math
from datetime import datetime
from telegram import Bot
from nepse_data_api import Nepse

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FIB_LEVELS = [0.618, 0.706, 0.79]


def is_common_stock(stock):
    symbol = stock["symbol"]
    name = stock["securityName"].upper()

    banned = [
        "PROMOTER",
        "DEBENTURE",
        "BOND",
        "MUTUAL",
        "FUND",
        "RIGHT",
        "PREFERENCE"
    ]

    if stock.get("activeStatus") != "A":
        return False

    if symbol.endswith("P"):
        return False

    for word in banned:
        if word in name:
            return False

    return True


def weekly_candles(data):
    weeks = {}
    for c in data:
        try:
            d = datetime.strptime(c["businessDate"], "%Y-%m-%d")
        except:
            continue

        key = (d.isocalendar().year, d.isocalendar().week)

        if key not in weeks:
            weeks[key] = {
                "open": c["openPrice"],
                "high": c["highPrice"],
                "low": c["lowPrice"],
                "close": c["closePrice"]
            }
        else:
            weeks[key]["high"] = max(
                weeks[key]["high"],
                c["highPrice"]
            )
            weeks[key]["low"] = min(
                weeks[key]["low"],
                c["lowPrice"]
            )
            weeks[key]["close"] = c["closePrice"]

    return list(weeks.values())


def swing_high_low(candles):
    highs = [x["high"] for x in candles]
    lows = [x["low"] for x in candles]

    return max(highs), min(lows)


def fibonacci(high, low):
    diff = high - low

    return {
        0.618: high - diff * 0.618,
        0.706: high - diff * 0.706,
        0.79: high - diff * 0.79
    } 
def score_stock(price, fibs):
    best = None
    best_level = None

    for level, value in fibs.items():
        diff = abs(price - value)

        if best is None or diff < best:
            best = diff
            best_level = level

    return best_level, best


def scan_stock(nepse, stock):

    try:

        history = nepse.get_historical_chart(stock["id"])

        if not history or len(history) < 40:
            return None

        candles = weekly_candles(history)

        if len(candles) < 20:
            return None

        high, low = swing_high_low(candles)

        fibs = fibonacci(high, low)

        price = candles[-1]["close"]

        level, distance = score_stock(price, fibs)

        if level is None:
            return None



             return {
            "symbol": stock["symbol"],
            "price": round(price, 2),
            "fib": level,
            "distance": round(distance, 2),
            "high": high,
            "low": low
        }
        


    except Exception as e:
        print(f"Error scanning {stock['symbol']}: {e}")
        return None

    

def format_message(results):

    if not results:
        return "📉 Weekly Scanner\n\nNo setups found."

    text = "📈 Weekly Fibonacci Scanner\n\n"

    for i, r in enumerate(results, start=1):

        text += (
            f"{i}. {r['symbol']}\n"
            f"Price : {r['price']}\n"
            f"Fib   : {r['fib']}\n"
            f"High  : {round(r['high'],2)}\n"
            f"Low   : {round(r['low'],2)}\n"
        f"Distance : {r['percent']}%\n"
f"Potential : {r['upside']}%\n\n")

    return text


async def main():

    bot = Bot(token=BOT_TOKEN)

    try:

        nepse = Nepse()

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

        print(e)


if __name__ == "__main__":
    asyncio.run(main())

