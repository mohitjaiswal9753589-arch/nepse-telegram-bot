import requests

BASE_URL = "https://www.nepalstock.com.np"

def get_security_list():
    url = f"{BASE_URL}/api/nots/security"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()

def get_chart_data(security_id):
    url = f"{BASE_URL}/api/nots/market/graphdata/{security_id}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()

