from typing import Union
from uuid import UUID
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.utils import is_uuid
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.storages import TmpStorage
from app.handlers.personal.keyboards import KeyboardSetUserContext, KeyKeyboard
from app.handlers.personal.user_settings.create_user_context import create_user_context


async def cmd_settings(
    event: Union[types.Message, types.CallbackQuery],
    state: FSMContext,
    tmp_storage: TmpStorage,
) -> None:
    await state.set_state(UserSettings.main)
    if isinstance(event, types.message.Message):
        # since the __init__ method is implemented as asynchronous, the creation of an instance of the class is
        # divided into two steps (I call the __new__ method on the first one - it has not changed, so it is taken
        # from the parent class, then the __init__ method is called for the created instance as asynchronous)
        kb = super(KeyboardSetUserContext, KeyboardSetUserContext).__new__(
            KeyboardSetUserContext
        )
        await kb.__init__(user_id=event.from_user.id)

        key = KeyKeyboard(
            bot_id=bot.id,
            chat_id=event.chat.id,
            user_id=event.from_user.id if event.from_user else None,
            message_id=event.message_id + 1,
        )
        # "Ховаємо" клавіатуру у глобальному об'єкті
        tmp_storage[key] = kb
        # виводимо клавіатуру
        await event.answer(
            text=tmp_storage[key].text,
            parse_mode="HTML",
            reply_markup=tmp_storage[key].markup(),
        )
    if isinstance(event, types.CallbackQuery):
        # we look at callback.data, depending on it:
        # or (the selected action provides a new keyboard in a new state)
        # - remove the existing keyboard from the global object
        # - call the appropriate handler
        # or (keyboard scroll)
        # - change the state of the keyboard in the global storage
        # - correct the message with the new keyboard
        key = KeyKeyboard(
            bot_id=bot.id,
            chat_id=event.message.chat.id if event.message.chat else None,
            user_id=event.from_user.id if event.from_user else None,
            message_id=event.message.message_id,
        )
        if event.data == "#CREATE_NEW_CONTEXT":
            await create_user_context(event, state, tmp_storage)
        elif event.data == "#DOWN":
            tmp_storage[key].markup_down()
        elif event.data == "#UP":
            tmp_storage[key].markup_up()
        elif event.data and is_uuid(event.data):
            user_context_id = UUID(event.data)
            await tmp_storage[key].set_existing_context(context_id=user_context_id)
            await event.message.edit_text(text=tmp_storage[key].text, parse_mode="HTML")
            await state.clear()
            del tmp_storage[key]
            return
        else:
            pass

        await event.message.edit_text(
            text=tmp_storage[key].text,
            reply_markup=tmp_storage[key].markup(),
            parse_mode="HTML",
        )
        await event.answer(show_alert=False)


def register_handler_settings(dp: Dispatcher) -> None:
    """
    Повинно спрацьовувати при (умова "або"):
    - команді "/settings"
    - будь-якому стані з класу UserSettings (пріоритет нижче ніж для команди /help)
    """
    dp.message.register(cmd_settings, Command(commands=["settings"]))
    dp.callback_query.register(cmd_settings, StateFilter(UserSettings.main))
