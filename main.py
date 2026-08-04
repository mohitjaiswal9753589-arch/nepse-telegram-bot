import os
import asyncio
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

    for candle in data:
        try:
            date = datetime.strptime(
                candle["businessDate"],
                "%Y-%m-%d"
            )
        except Exception:
            continue

        key = (
            date.isocalendar().year,
            date.isocalendar().week
        )

        if key not in weeks:
            weeks[key] = {
                "open": candle["openPrice"],
                "high": candle["highPrice"],
                "low": candle["lowPrice"],
                "close": candle["closePrice"]
            }
        else:
            weeks[key]["high"] = max(
                weeks[key]["high"],
                candle["highPrice"]
            )
            weeks[key]["low"] = min(
                weeks[key]["low"],
                candle["lowPrice"]
            )
            weeks[key]["close"] = candle["closePrice"]

    return list(weeks.values())


def swing_high_low(candles):
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]

    return max(highs), min(lows)


def fibonacci(high, low):
    diff = high - low

    return {
        0.618: high - diff * 0.618,
        0.706: high - diff * 0.706,
        0.79: high - diff * 0.79
    }


def score_stock(price, fibs):
    best_level = None
    best_distance = None

    for level, fib_price in fibs.items():
        distance = abs(price - fib_price)

        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_level = level

    return best_level, best_distance

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

        percent = (distance / price) * 100
        upside = ((high - price) / price) * 100

        return {
            "symbol": stock["symbol"],
            "price": round(price, 2),
            "fib": level,
            "distance": round(distance, 2),
            "percent": round(percent, 2),
            "upside": round(upside, 2),
            "high": high,
            "low": low
        }

    except Exception as e:
        print(f"Error scanning {stock['symbol']}: {e}")
        return None


def scan_market(nepse):
    stocks = nepse.get_security_list()

    results = []

    for stock in stocks:
        if not is_common_stock(stock):
            continue

        result = scan_stock(nepse, stock)

        if result:
            results.append(result)

    results.sort(
        key=lambda x: x["upside"],
        reverse=True
    )

    return results[:5]

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
        print(f"Telegram Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    
    
