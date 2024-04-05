import os

import requests
from bs4 import BeautifulSoup
import shutil

from bot_utils.chatgpt.gigachat.token_worker import get_access_token


async def get_images_from_gigachats_answer(answer: str) -> tuple:
    access_token_data = await get_access_token()
    if access_token_data[0] == 200:
        access_token = access_token_data[1]
    else:
        return False, []
    soup = BeautifulSoup(answer, "html.parser")
    image_links = list(map(
        lambda tag: (tag.get("src"), f'https://gigachat.devices.sberbank.ru/api/v1/files/{tag.get("src")}/content'),
        soup.find_all("img")
    ))
    image_paths = []
    if not os.path.isdir('images'):
        os.mkdir('images')
    for image_data in image_links:
        name, url = image_data
        headers = {
            'Accept': 'application/jpg',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.request("GET", url, headers=headers, stream=True)
        if response.status_code == 200:
            filepath = f"images/{name}.jpg"
            with open(filepath, "wb") as output:
                try:
                    shutil.copyfileobj(response.raw, output)
                    image_paths.append(filepath)
                except Exception:
                    pass
        del response
    return bool(image_paths), image_paths


async def delete_images() -> None:
    try:
        shutil.rmtree("images")
    except Exception as e:
        print(e)
