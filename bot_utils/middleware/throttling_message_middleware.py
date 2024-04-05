# импорты aiogram
from aiogram import BaseMiddleware
from aiogram import types
from aiogram.fsm.storage.redis import RedisStorage
# импорты из других библиотек
from typing import Any, Awaitable, Callable, Dict
from math import ceil, floor
from threading import Thread
# импорты из файлов
from bot_utils.middleware.messages_deleter import delete_messages_by_timer


class ThrottlingMessageMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage, message_limit=1):
        self.storage = storage
        self.message_limit = message_limit

    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = f"message_from_{event.from_user.id}"
        check = await self.storage.redis.get(name=throttling_key)
        if check:
            if check == '0':
                message2 = None
                try:
                    if event.content_type == 'text':
                        await self.storage.redis.set(name=throttling_key, value=1, ex=self.message_limit)
                        message2 = await event.reply(f"{event.from_user.first_name}, слишком много запросов, повторите через {ceil(self.message_limit)} секунду(ы)!")
                except Exception:
                    pass
                Thread(target=delete_messages_by_timer, args=(2, event.bot.token, event, message2)).start()
            elif check == '6':
                await self.storage.redis.set(name=throttling_key, value='ban', ex=300)
                await event.answer(f"⛔️ {event.from_user.first_name}, бан на 5 минут за флуд!")
                Thread(target=delete_messages_by_timer, args=(0.5, event.bot.token, event)).start()
            elif check != 'ban':
                value = 1
                if check.isdigit():
                    value += int(check)
                await self.storage.redis.set(name=throttling_key, value=value, ex=self.message_limit)
                Thread(target=delete_messages_by_timer, args=(0.5, event.bot.token, event)).start()
            return
        await self.storage.redis.set(name=throttling_key, value=0, ex=self.message_limit)
        return await handler(event, data)
