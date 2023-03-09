from typing import Union
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.db_functions.personal import get_context
from app.storages import TmpStorage
from app.handlers.personal.keyboards import CombiKeyboardGenerator, KeyKeyboard

async def create_user_comtext(
    callback: types.CallbackQuery,
    state: FSMContext,
    tmp_storage: TmpStorage
) -> None:
    await state.set_state(UserSettings.create_new_user_context)
    contexts = await get_context()
    print(contexts)
