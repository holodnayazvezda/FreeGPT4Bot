from random import choice

from aiogram import types
from aiogram.enums import ReactionTypeType
from aiogram.types import ReactionTypeEmoji

from data import AVAILABLE_REACTIONS


async def set_random_reaction(message: types.Message):
    await message.react([
        ReactionTypeEmoji(
            type=ReactionTypeType.EMOJI,
            emoji=choice(AVAILABLE_REACTIONS)
        )
    ])
