# импорты aiogram
from aiogram import BaseMiddleware
from aiogram import types
from aiogram.fsm.storage.redis import RedisStorage
# импорты из других библиотек
from typing import Any, Awaitable, Callable, Dict
from math import floor


class ThrottlingCallMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage, call_limit=2):
        self.storage = storage
        self.call_limit = call_limit

    async def __call__(
            self,
            handler: Callable[[types.CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: types.CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        throttling_key = f"call_from_{event.from_user.id}"
        check = await self.storage.redis.get(name=throttling_key)
        if check:
            if check == '0':
                await self.storage.redis.set(name=throttling_key, value=1, ex=self.call_limit)
                try:
                    await event.answer(f"Cлишком много запросов, повторите через {floor(self.call_limit)} секунду(ы)!")
                except Exception:
                    pass
            elif check == '6':
                await self.storage.redis.set(name=throttling_key, value='ban', ex=300)
                try:
                    await event.answer("⛔️ Бан на 5 минуты за флуд!", show_alert=True)
                except Exception:
                    pass
            elif check != 'ban':
                value = 1
                if check.isdigit():
                    value += int(check)
                await self.storage.redis.set(name=throttling_key, value=value, ex=self.call_limit)
            return
        await self.storage.redis.set(name=throttling_key, value=0, ex=self.call_limit)
        return await handler(event, data)
