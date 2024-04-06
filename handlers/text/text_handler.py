from aiogram import types

from handlers.bot_info import BotInfo
from handlers.gpt.gpt_functions import add_user_to_queue_and_start_generating
from handlers.gpt.gpt_message_functions import clear_chat_gpt_conversation, change_gpt_version


async def text_messages_handler(message: types.Message, bot_instance: BotInfo, users_temp_data_dict: dict):
    if message.text == "🗑 Очистить историю диалога":
        await clear_chat_gpt_conversation(message, bot_instance)
    elif "Переключиться на" in message.text:
        await change_gpt_version(message, bot_instance, users_temp_data_dict)
    else:
        await add_user_to_queue_and_start_generating(message, bot_instance, users_temp_data_dict)
