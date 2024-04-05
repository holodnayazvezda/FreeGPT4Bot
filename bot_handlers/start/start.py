from aiogram import types
from aiogram.utils import keyboard

from bot_handlers.bot_info import BotInfo
from bot_utils.database.folder_worker import get_dictionary
from bot_utils.get_button_list import get_button_list_for_selected_model
from bot_utils.text_workers.get_message_text import welcome_user


async def start(message: types.Message, bot_instance: BotInfo) -> None:
    users_temp_data_dict = await get_dictionary(str(message.from_user.id), bot_instance.bot_id, 2)
    markup_builder = keyboard.ReplyKeyboardBuilder()
    markup_builder.button(text="🗑 Очистить историю диалога")
    model = 'gpt-3.5-turbo' if 'selected_model' not in users_temp_data_dict \
        else users_temp_data_dict['selected_model']
    for btn_text in (await get_button_list_for_selected_model(model)):
        markup_builder.button(text=btn_text)
    markup_builder.adjust(1)
    markup = markup_builder.as_markup(resize_keyboard=True)
    await message.answer(text=await welcome_user(message), reply_markup=markup, parse_mode="markdown")
