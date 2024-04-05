from aiogram import types

from bot_utils.users.amount_of_users_getter import get_amount_of_users


async def welcome_user(message: types.Message) -> str:
    f = open(file="./bot_data/message_texts/welcome.txt", mode="r+", encoding="utf-8")
    message_text = f.read().format(message.from_user.first_name)
    f.close()
    return message_text


async def get_gpt_request_limit_text(available_amount_of_requests: int, model: str) -> str:
    f = open(file="./bot_data/message_texts/gpt_requests_limit_has_been_reached.txt", mode="r+", encoding="utf-8")
    message_text = f.read().format(available_amount_of_requests, model, model.capitalize())
    f.close()
    return message_text


async def get_statistics_text() -> str:
    f = open(file="./bot_data/message_texts/statistics.txt", mode="r+", encoding="utf-8")
    amount_of_users = await get_amount_of_users()
    message_text = f.read().format(amount_of_users['total'], amount_of_users['daily'])
    f.close()
    return message_text
