from typing import Optional, Union
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.handlers.personal.user_settings import UserSettings
from app.create_bot import bot


async def cmd_settings(
        event: Union[types.Message, types.CallbackQuery],
        state: Optional[FSMContext] = None,
    ) -> None:
    print("in cmd_settings".center(120, "-"))
    print(f"type(event) = {type(event)}")
    print(f"event: {event}")
    print(f"type(state) = {type(state)}")
    print(f"res isinstance Message: {isinstance(event, types.Message)}")
    buttons = [
        [types.InlineKeyboardButton(text="UP", callback_data="#UP")],
        [types.InlineKeyboardButton(text="DOWN", callback_data="#DOWN")]
        ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.set_state(UserSettings.main)
    if isinstance(event, types.message.Message):
        await event.answer("it is message", reply_markup=kb)
    print(f"res isinstance CallbackQuery: {isinstance(event, types.CallbackQuery)}")
    if isinstance(event, types.CallbackQuery):
        await event.answer("it is CallbackQuery")

    await event.answer("There will be settings-block")



def register_handler_settings(dp: Dispatcher) -> None:
    """
    Повинно спрацьовувати при (умова "або"):
    - команді "/settings"
    - будь-якому стані з класу UserSettings (пріоритет нижче ніж для команди /help)
    """
    dp.message.register(cmd_settings, Command(commands=["settings"]))
    dp.message.register(cmd_settings, StateFilter(UserSettings))
