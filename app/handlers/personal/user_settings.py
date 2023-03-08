from typing import Optional
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class UserSettings(StatesGroup):
    main = State()
    user_context = State()
    set_actual_user_context = State()
    create_new_user_context = State()
    move_to_archive_user_context = State()
    extract_from_archive_user_cintext = State()


async def user_context_menu(
    message: types.Message,
    state: Optional[FSMContext],
    callback: Optional[types.CallbackQuery] = None,
) -> None:
    # встановити статус
    # get user_contexts
    # get user settings language (from DB or from TG)
    # gen dict with possible messages (depends on status, current language)
    # create current list of keys for keyboard
    # call handler for
    await message.answer("There will be settings-block")


# def register_handler_settings(dp: Dispatcher) -> None:
#     dp.message.register(user_context_menu, Command(commands=["settings"]))
