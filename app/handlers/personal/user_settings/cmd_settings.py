from typing import Union
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.utils import is_uuid
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.db_functions.personal import get_user_context
from app.storages import TmpStorage
from app.handlers.personal.keyboards import KeyboardSetUserContext, KeyKeyboard
from app.handlers.personal.user_settings.create_user_context import create_user_context


async def cmd_settings(
    event: Union[types.Message, types.CallbackQuery],
    state: FSMContext,
    tmp_storage: TmpStorage,
) -> None:
    print("in cmd_settings".center(120, "-"))
    print(f"tmp_storage: {tmp_storage}")
    print(f"type of tmp_storage: {type(tmp_storage)}")
    print(f"id of tmp_storage: {id(tmp_storage)}")
    await state.set_state(UserSettings.main)
    print(f"STATE: {await state.get_state()}")
    user_contexts = await get_user_context(event.from_user.id)
    if isinstance(event, types.message.Message):
        # отримати отсортований за lastdate список всіх статусів користувача (GET user_contexts/)
        # формуємо список кнопок для клавіатури, створюємо клавіатуру (personal.keyboards.CombiKeyboardGenerator).
        print(f"event is Message, message_id: {event.message_id}")
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
            message_id=event.message_id,
        )
        print(f"key for keyboard is: {key}")
        # "Ховаємо" клавіатуру у глобальному об'
        tmp_storage[key] = kb
        print(f"tmp_storage after add kb: {tmp_storage}")
        # виводимо клавіатуру
        text = (
            user_contexts[0]["context_1"]["name"]
            + "-"
            + user_contexts[0]["context_2"]["name"]
        )
        await event.answer(
            text=f"<b>{text}</b>",
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
        if event.data == "#CREATE_NEW_CONTEXT":
            await create_user_context(event, state, tmp_storage)
        elif event.data == "#SET_CURRENT_CONTEXT":
            pass
        elif event.data == "#SEND_TO_ARCHIVE":
            pass
        elif event.data == "#EXTRACT_FROM_ARCHIVE":
            pass
        elif event.data == "#DOWN":
            pass
        elif event.data == "#UP":
            pass
        elif event.data and is_uuid(event.data):
            pass
        else:
            pass
        await event.answer(f"callback.data is: {event.data}")


def register_handler_settings(dp: Dispatcher) -> None:
    """
    Повинно спрацьовувати при (умова "або"):
    - команді "/settings"
    - будь-якому стані з класу UserSettings (пріоритет нижче ніж для команди /help)
    """
    dp.message.register(cmd_settings, Command(commands=["settings"]))
    dp.callback_query.register(cmd_settings, StateFilter(UserSettings.main))
