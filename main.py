import requests

API_URL = "https://nepse-data-api.vercel.app/api/history"

def test_data():
    symbol = "NABIL"

    response = requests.get(
        API_URL,
        params={"symbol": symbol}
    )

    print(response.status_code)
    print(response.text[:500])

test_data()
