from aiogram import types
from telebot import TeleBot
import time


def delete_messages_by_timer(delay: float, bot_token: str, message1: types.Message, message2: types.Message = None) -> None:
    time.sleep(delay)
    bot_telebot = TeleBot(token=bot_token)
    if message2:
        try:
            bot_telebot.delete_message(chat_id=message2.chat.id, message_id=message2.message_id)
        except Exception:
            pass
    try:
        bot_telebot.delete_message(chat_id=message1.chat.id, message_id=message1.message_id)
    except Exception:
        pass