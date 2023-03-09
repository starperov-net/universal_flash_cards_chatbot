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

