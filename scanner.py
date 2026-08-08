from datetime import datetime
from nepse_data_api import Nepse

nepse = Nepse()


def get_stocks():
    return nepse.get_security_list()


def get_history(stock_id):
    try:
        history = nepse.get_historical_chart(stock_id)

        print(
            "HISTORY",
            stock_id,
            len(history) if history else 0
        )

        return history or []

    except Exception as e:
        print("HISTORY ERROR", stock_id, e)
        return []


def is_common_stock(stock):
    symbol = stock.get("symbol", "")
    name = stock.get("securityName", "").upper()

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

    return not any(word in name for word in banned)


def weekly_candles(data):
    weeks = {}

    for candle in data:
        try:
            d = datetime.strptime(
                candle["businessDate"],
                "%Y-%m-%d"
            )

            key = (
                d.isocalendar().year,
                d.isocalendar().week
            )

            open_price = float(candle["openPrice"])
            high = float(candle["highPrice"])
            low = float(candle["lowPrice"])
            close = float(candle["closePrice"])

        except (KeyError, TypeError, ValueError):
            continue

        if key not in weeks:
            weeks[key] = {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close
            }

        else:
            weeks[key]["high"] = max(
                weeks[key]["high"],
                high
            )

            weeks[key]["low"] = min(
                weeks[key]["low"],
                low
            )

            weeks[key]["close"] = close

    return [
        weeks[key]
        for key in sorted(weeks)
    ]


def swing_high_low(candles):
    highs = [
        c["high"]
        for c in candles
    ]

    lows = [
        c["low"]
        for c in candles
    ]

    return max(highs), min(lows)


def fibonacci(high, low):
    diff = high - low

    return {
        0.618: high - diff * 0.618,
        0.706: high - diff * 0.706,
        0.790: high - diff * 0.790
    }


def score_stock(price, fibs):

    best_level = None
    best_distance = None

    for level, value in fibs.items():

        distance = abs(
            price - value
        )

        if (
            best_distance is None
            or distance < best_distance
        ):
            best_level = level
            best_distance = distance

    return best_level, best_distance


def scan_stock(stock):

    try:

        history = get_history(
            stock["id"]
        )

        if len(history) < 40:
            return None

        candles = weekly_candles(
            history
        )

        if len(candles) < 20:
            return None

        high, low = swing_high_low(
            candles
        )

        if high <= low:
            return None

        fibs = fibonacci(
            high,
            low
        )

        price = candles[-1]["close"]

        if price <= 0:
            return None

        level, distance = score_stock(
            price,
            fibs
        )

        if level is None:
            return None

        percent = (
            distance / price
        ) * 100

        upside = (
            (high - price)
            / price
        ) * 100

        # Maximum distance from Fibonacci level:
        # 1.5% of price or Rs. 2, whichever is greater.

        tolerance = max(
            price * 0.015,
            2
        )

        if distance > tolerance:
            return None

        return {
            "symbol": stock["symbol"],
            "price": round(price, 2),
            "fib": level,
            "distance": round(distance, 2),
            "percent": round(percent, 2),
            "upside": round(upside, 2),
            "high": round(high, 2),
            "low": round(low, 2)
        }

    except Exception as e:

        print(
            f"Error scanning "
            f"{stock.get('symbol', 'UNKNOWN')}: {e}"
        )

        return None


def scan_market():

    stocks = get_stocks()

    results = []

    print(
        "Total stocks:",
        len(stocks)
    )

    for stock in stocks:

        if not is_common_stock(stock):
            continue

        result = scan_stock(
            stock
        )

        if result:
            results.append(
                result
            )

    results.sort(
        key=lambda x: x["upside"],
        reverse=True
    )

    print(
        "Total setups found:",
        len(results)
    )

    return results
