from datetime import date, datetime
from nepse_data_api import Nepse

nepse = Nepse()

today = date.today().strftime("%Y-%m-%d")
START_DATE = "2025-01-01"

def get_stocks():
    return nepse.get_security_list()
def get_history(stock_id):
    try:
        history = nepse.get_historical_chart(
            stock_id,
            start_date=START_DATE,
            end_date=today
        )

        print("HISTORY", stock_id, len(history) if history else 0)

        return history

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
        except Exception:
            continue

        key = (
            d.isocalendar().year,
            d.isocalendar().week
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

    for level, value in fibs.items():
        distance = abs(price - value)

        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_level = level

    return best_level, best_distance

def scan_stock(stock):
    try:
        history = get_history(stock["id"])

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

def scan_market():
    stocks = get_stocks()

    test_stock = next(
        (s for s in stocks if s.get("symbol") == "EBL"),
        None
    )

    if test_stock:
        print("TESTING:", test_stock["symbol"], test_stock["id"])
        print("TEST HISTORY:", get_history(test_stock["id"]))

    return []
    
