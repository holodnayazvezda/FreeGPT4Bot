import os
import subprocess

from aiogram import types
from telebot import types as tb_types

from bot_data.config import MODELS_DATA
from bot_handlers.bot_info import BotInfo
from bot_handlers.gpt.gpt_message_functions import delete_messages
from bot_utils.chatgpt.gigachat.ask_gigachat import ask_gigachat
from bot_utils.chatgpt.gigachat.gigachat_image_worker import delete_images
from bot_utils.chatgpt.gpt4free_worker import *
from bot_utils.database.folder_worker import get_dictionary, create_or_dump_user
from bot_utils.recognizers.audio_to_text import audio_to_text
from bot_utils.recognizers.image_to_text import get_text_from_image
from bot_utils.text_workers.get_message_text import get_gpt_request_limit_text

# глобальная переменная задачи перебора пользователей, спрашивающих gpt-4
on_processing_gpt4_requests = False
# глобальная переменная для хранения промптов к gpt-4-turbo и их id
chats_ids_and_prompts_of_gpt4_requests = {}
# глобальная переменная задачи перебора пользователей, спрашивающих GigaChat
on_processing_gigachat_requests = False
# глобальная переменная для хранения промптов к GigaChat и их id
chats_ids_and_prompts_of_gigachat_requests = {}


async def unsuccessful_request_to_chatgpt(chat_id: int, user_id: int, message_text: str, bot_instance: BotInfo) -> None:
    try:
        response = await ask_chat_gpt_temporary_api(message_text, user_id)
        if response:
            bot_instance.bot_telebot.send_message(chat_id=chat_id, text=response, parse_mode='markdown')
        else:
            raise Exception('The answer is empty')
    except Exception:
        bot_instance.bot_telebot.send_message(chat_id=chat_id, text='🛑 Возникла ошибка при получении ответа! '
                                                                    'Повторите попытку через несколько минут.')


async def start_users_processing_or_generating_answer(model: str, message: types.Message, prompt: str,
                                                      bot_instance: BotInfo) -> None:
    global on_processing_gpt4_requests, chats_ids_and_prompts_of_gpt4_requests, \
        on_processing_gigachat_requests, chats_ids_and_prompts_of_gigachat_requests
    if model == "gpt-4-turbo":
        chats_ids_and_prompts_of_gpt4_requests[message.chat.id] = [message.from_user.id, prompt, bot_instance]
        if not on_processing_gpt4_requests:
            on_processing_gpt4_requests = True
            Thread(target=async_functions_process_starter, args=(process_gpt4_users, [])).start()
    elif model == 'gpt-3.5-turbo':
        Thread(target=async_functions_process_starter, args=(generate_and_send_answer, [
            message.chat.id, message.from_user.id, prompt, bot_instance])).start()
    else:
        chats_ids_and_prompts_of_gigachat_requests[message.chat.id] = [message.from_user.id, prompt, bot_instance]
        if not on_processing_gigachat_requests:
            on_processing_gigachat_requests = True
            Thread(target=async_functions_process_starter, args=(process_gigachat_users, [])).start()


async def generate_and_send_answer(chat_id: int, user_id: int, message_text: str, bot_instance: BotInfo) -> None:
    bot_instance.bot_telebot.send_chat_action(chat_id=chat_id, action='typing')
    users_temp_data_dict = await get_dictionary(str(user_id), bot_instance.bot_id, 2)
    try:
        model = 'gpt-3.5-turbo'
        if 'selected_model' in users_temp_data_dict and users_temp_data_dict['selected_model']:
            model = users_temp_data_dict['selected_model']
        if model == 'gpt-4-turbo':
            response = await ask_chat_gpt_4(prompt=message_text, user_id=user_id)
        elif model == 'gpt-3.5-turbo':
            response = await ask_chat_gpt_and_return_answer(model, prompt=message_text, user_id=user_id)
        else:
            response = await ask_gigachat(prompt=message_text, user_id=user_id)
        if response[1] == 808:
            media_group = []
            image_files = []
            for image_path in response[0]:
                image_file = open(image_path, "rb")
                media_group.append(
                    tb_types.InputMediaPhoto(
                        media=image_file,
                        parse_mode="file"
                    )
                )
                image_files.append(image_file)
            bot_instance.bot_telebot.send_media_group(chat_id=chat_id, media=media_group)
            for image_file in image_files:
                image_file.close()
            await delete_images()
        elif response[1] == 200:
            bot_instance.bot_telebot.send_message(chat_id=chat_id, text=response[0], parse_mode='markdown')
        else:
            if response[1] == 400:
                bot_instance.bot_telebot.send_message(chat_id=chat_id,
                                                      text="⚠️ Ваш запрос слишком длинный! Пожалуйста, сократите "
                                                           "запрос, что бы бот смог обработать его.",
                                                      parse_mode='markdown')
            else:
                await unsuccessful_request_to_chatgpt(chat_id, user_id, message_text, bot_instance)
    except Exception:
        await unsuccessful_request_to_chatgpt(chat_id, user_id, message_text, bot_instance)


async def add_user_to_queue_and_start_generating(message: types.Message, bot_instance: BotInfo,
                                                 users_temp_data_dict: dict) -> None:
    try:
        model = users_temp_data_dict['selected_model']
    except KeyError:
        model = 'gpt-3.5-turbo'
    table_name = MODELS_DATA[f'🔁 Переключиться на {model}']['quantity_of_req_table_name']
    amount_of_requests = await get_amount_of_requests_for_user('./bot_data/databases/quantity_of_requests.sqlite3',
                                                               table_name, message.from_user.id)
    available_amount_of_requests = await get_available_amount_of_requests_to_chat_gpt(model)
    if amount_of_requests < available_amount_of_requests:
        if message.text:
            await start_users_processing_or_generating_answer(model, message, message.text, bot_instance)
        elif message.voice:
            if not os.path.isdir('voice'):
                os.mkdir('voice')
            try:
                voice = await bot_instance.bot.get_file(message.voice.file_id)
                await bot_instance.bot.download_file(voice.file_path, voice.file_path)
                Thread(target=async_functions_process_starter, args=(translate_audio_to_text_and_start_generating,
                                                                     [message, voice.file_path, model,
                                                                      bot_instance])).start()
            except Exception:
                pass
        else:
            if message.media_group_id:
                if ('last_chat_gpt_photo_media' in users_temp_data_dict and
                        message.media_group_id == users_temp_data_dict['last_chat_gpt_photo_media']):
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    return
                users_temp_data_dict['last_chat_gpt_photo_media'] = message.media_group_id
                Thread(target=async_functions_process_starter,
                       args=(create_or_dump_user, [str(message.from_user.id), bot_instance.bot_id,
                                                   str(users_temp_data_dict), 2])).start()
            try:
                Thread(target=async_functions_process_starter,
                       args=(get_text_from_image_and_start_generating,
                             [message, (await bot_instance.bot.get_file(message.photo[-1].file_id)).file_path, model,
                              bot_instance])).start()
            except Exception as e:
                print(e)
                pass
    else:
        gpt_request_limit_message = await message.reply(
            text=await get_gpt_request_limit_text(available_amount_of_requests, model), parse_mode="markdown")
        Thread(target=delete_messages, args=(20, message.chat.id, message.message_id,
                                             gpt_request_limit_message.message_id, bot_instance.bot_telebot)).start()


async def get_text_from_image_and_start_generating(message: types.Message, filepath, model: str,
                                                   bot_instance: BotInfo) -> None:
    amount_of_unsucessful_requests_to_ocr_api = await get_amount_of_requests_for_user(
        "./bot_data/databases/quantity_of_requests.sqlite3",
        "quantity_of_unsuccessful_requests_to_ocr_space", message.from_user.id)
    if amount_of_unsucessful_requests_to_ocr_api < 30:
        bot_instance.bot_telebot.send_chat_action(chat_id=message.chat.id, action='upload_photo')
        image_url = f'https://api.telegram.org/file/bot{bot_instance.token}/{filepath}'
        data = await get_text_from_image(message.from_user.id, image_url, 15)
        if data:
            await start_users_processing_or_generating_answer(model, message, data, bot_instance)
    else:
        message_id = bot_instance.bot_telebot.send_message(
            chat_id=message.chat.id,
            text='⚠️ Количество ошибок при распознавании текста с изображений достигло 30. Попробуйте еще раз *после '
                 '00:00 по МСК*!',
            parse_mode='markdown').message_id
        Thread(target=delete_messages, args=(20, message.chat.id, message.message_id, message_id,
                                             bot_instance.bot_telebot)).start()


async def translate_audio_to_text_and_start_generating(message: types.Message, voice_file_path_oga: str, model: str,
                                                       bot_instance: BotInfo) -> None:
    voice_file_path_wav = ""
    try:
        bot_instance.bot_telebot.send_chat_action(chat_id=message.chat.id, action='upload_voice')
        if message.voice.file_size / (1024 * 1024) > 5:
            raise Exception('The weight of the audiofile is more that 5M')
        if message.voice.duration > 90:
            raise Exception('The length of the audiofile is more that 90 seconds')
        voice_file_path_wav = voice_file_path_oga.replace('.oga', '.wav')
        subprocess.run(['ffmpeg', '-i', voice_file_path_oga, voice_file_path_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        data = audio_to_text(voice_file_path_wav)
        try:
            os.remove(voice_file_path_oga)
        except Exception:
            pass
        try:
            os.remove(voice_file_path_wav)
        except Exception:
            pass
        await start_users_processing_or_generating_answer(model, message, data, bot_instance)
    except Exception as e:
        if 'The length of the audiofile is more that 90 seconds' in str(e):
            audio_translating_error_text = ('⚠️ Длинна голосового сообщения превышает 1.5 минуты! Оно не может быть '
                                            'обработано.')
        elif 'The weight of the audiofile is more that 5M' in str(e):
            audio_translating_error_text = \
                '⚠️ Вес голосового сообщения не может превышать 5 мегабайт! Оно не может быть обработано.'
        else:
            audio_translating_error_text = ('🛑 Не удалось распознать текст голосового сообщения, пожалуйста, '
                                            'попробуйте еще раз.')
        message_id = bot_instance.bot_telebot.send_message(chat_id=message.chat.id,
                                                           text=audio_translating_error_text).message_id
        if voice_file_path_oga:
            try:
                os.remove(voice_file_path_oga)
            except Exception:
                pass
        if voice_file_path_wav:
            try:
                os.remove(voice_file_path_wav)
            except Exception:
                pass
        Thread(target=delete_messages, args=(5, message.chat.id, message.message_id, message_id,
               bot_instance.bot_telebot)).start()


async def process_gpt4_users() -> None:
    global on_processing_gpt4_requests, chats_ids_and_prompts_of_gpt4_requests
    while True:
        for chat_id, message_data in list(chats_ids_and_prompts_of_gpt4_requests.items()):
            del chats_ids_and_prompts_of_gpt4_requests[chat_id]
            await generate_and_send_answer(chat_id, message_data[0], message_data[1], message_data[2])
        if len(chats_ids_and_prompts_of_gpt4_requests) == 0:
            on_processing_gpt4_requests = False
            return


async def process_gigachat_users() -> None:
    global on_processing_gigachat_requests, chats_ids_and_prompts_of_gigachat_requests
    while True:
        for chat_id, message_data in list(chats_ids_and_prompts_of_gigachat_requests.items()):
            del chats_ids_and_prompts_of_gigachat_requests[chat_id]
            await generate_and_send_answer(chat_id, message_data[0], message_data[1], message_data[2])
        if len(chats_ids_and_prompts_of_gigachat_requests) == 0:
            on_processing_gigachat_requests = False
            return
