from bot_data.config import GIGACHAT_CLIENT_SECRET

import requests

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload = 'scope=GIGACHAT_API_PERS'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': '6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e',
    'Authorization': f'Basic {GIGACHAT_CLIENT_SECRET}',
}


async def get_access_token() -> tuple:
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return 200, dict(response.json())['access_token']
    else:
        return response.status_code, ""
