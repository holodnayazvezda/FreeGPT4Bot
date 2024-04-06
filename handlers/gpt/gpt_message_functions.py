import time
from threading import Thread

from aiogram import types
from aiogram.utils import keyboard
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException

from data.config import MODELS_DATA
from handlers.bot_info import BotInfo
from utils.async_process_runner import async_functions_process_starter
from utils.chatgpt.chat_gpt_users_worker import clear_history_of_requests
from utils.chatgpt.requests_counter import get_amount_of_requests_for_user, get_available_amount_of_requests_to_chat_gpt
from utils.database.folder_worker import create_or_dump_user
from utils.get_button_list import get_button_list_for_selected_model


async def clear_chat_gpt_conversation(message, bot_instance: BotInfo):
    Thread(target=async_functions_process_starter, args=(clear_history_of_requests,
                                                         ['./data/databases/history_of_requests_to_chatgpt.sqlite3',
                                                          'users_history', message.from_user.id])).start()
    await bot_instance.bot.send_message(chat_id=message.chat.id, text="✅ История диалога очищена")


async def change_gpt_version(message: types.Message, bot_instance: BotInfo, users_temp_data_dict: dict) -> None:
    selected_model = MODELS_DATA[message.text]['name']
    users_temp_data_dict['selected_model'] = selected_model
    table_name = MODELS_DATA[message.text]['quantity_of_req_table_name']
    available_amount_of_requests = await get_available_amount_of_requests_to_chat_gpt(selected_model)
    amount_of_requests = await get_amount_of_requests_for_user('./data/databases/quantity_of_requests.sqlite3',
                                                               table_name, message.from_user.id)
    rest_of_requests = available_amount_of_requests - amount_of_requests
    message_text = f'✅ Вы переключились на модель: *{selected_model}*.\n\n'
    if rest_of_requests > 0:
        message_text += (f'⏳ Сегодня вы можете задать ей вопрос еще *{rest_of_requests} раз(а)*.\n\nℹ️ Ваш лимит для '
                         f'выбранной модели составляет *{available_amount_of_requests}* запросов в день.')
    else:
        message_text += (f'❗️ Вы достигли дневного лимита в {available_amount_of_requests} запросов к выбранной '
                         f'модели. Она вновь сможет отвечать на ваши запросы завтра.')
    markup_builder = keyboard.ReplyKeyboardBuilder()
    markup_builder.button(text='🗑 Очистить историю диалога')
    for btn_text in await get_button_list_for_selected_model(selected_model):
        markup_builder.button(text=btn_text)
    markup_builder.adjust(1)
    markup = markup_builder.as_markup(resize_keyboard=True)
    await message.answer(message_text, reply_markup=markup, parse_mode="markdown")
    Thread(target=async_functions_process_starter,
           args=(create_or_dump_user,
                 [str(message.from_user.id), bot_instance.bot_id, str(users_temp_data_dict),  2])).start()


def delete_messages(delay, chat_id: int, users_message_id: int, bots_message_id: int, bot_telebot: TeleBot) -> None:
    time.sleep(delay)
    try:
        bot_telebot.delete_message(chat_id=chat_id, message_id=users_message_id)
    except ApiTelegramException:
        pass
    if bots_message_id is not None:
        try:
            bot_telebot.delete_message(chat_id=chat_id, message_id=bots_message_id)
        except ApiTelegramException:
            pass
