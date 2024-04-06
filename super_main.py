import asyncio
from threading import Thread

from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.storage.redis import RedisStorage
from telebot import TeleBot

from data.config import REDIS_URL, TEST_TOKENS
from handlers.start.start import start
from handlers.statistics.statistics import statistics
from handlers.text.text_handler import *
from utils.database.folder_worker import get_dictionary
from utils.filters.is_admin_filter import IsAdmin
from utils.middleware.throttling_call_middleware import ThrottlingCallMiddleware
from utils.middleware.throttling_message_middleware import ThrottlingMessageMiddleware
from utils.updater import update_g4f_package
from utils.users.users_registrator import register_user

# создаем объект хранилища
redis_storage = RedisStorage.from_url(
    url=REDIS_URL,
    connection_kwargs={"decode_responses": True}
)


async def bot_init(token: str) -> None:
    dp = Dispatcher(storage=redis_storage)
    dp.message.middleware(ThrottlingMessageMiddleware(redis_storage))
    dp.callback_query.middleware(ThrottlingCallMiddleware(redis_storage))

    bot = Bot(token=token)
    bot_telebot = TeleBot(token=token)
    bot_id = int(token.split(':')[0])
    bot_instance = BotInfo(bot=bot, bot_telebot=bot_telebot, bot_id=bot_id, token=token)

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        Thread(target=register_user, args=(message.from_user.id,)).start()
        await start(message, bot_instance)

    @dp.message(Command(commands="stat"), IsAdmin())
    async def get_statistics_info(message: types.Message):
        Thread(target=register_user, args=(message.from_user.id,)).start()
        await statistics(message)

    @dp.message(F.text | F.photo | F.voice)
    async def chatgpt_message_handler(message: types.Message):
        Thread(target=register_user, args=(message.from_user.id,)).start()
        users_temp_data_dict = await get_dictionary(str(message.from_user.id), bot_id, 2)
        if message.text:
            await text_messages_handler(message, bot_instance, users_temp_data_dict)
        else:
            await add_user_to_queue_and_start_generating(message, bot_instance, users_temp_data_dict)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    print(f'{len(TEST_TOKENS)} bot(s) connected to FreeChatGPT engine')
    tasks = []
    for token in TEST_TOKENS:
        task = asyncio.create_task(bot_init(token))
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        Thread(target=update_g4f_package, args=(59,)).start()
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
