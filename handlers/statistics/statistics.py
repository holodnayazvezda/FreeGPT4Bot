from aiogram import types

from utils.text_workers.get_message_text import get_statistics_text


async def statistics(message: types.Message) -> None:
    await message.answer(
        text=await get_statistics_text(),
        parse_mode="markdown"
    )
