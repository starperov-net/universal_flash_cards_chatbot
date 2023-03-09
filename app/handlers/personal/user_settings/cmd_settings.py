from typing import Union
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.db_functions.personal import get_user_context
from app.storages import TmpStorage
from app.handlers.personal.keyboards import CombiKeyboardGenerator, KeyKeyboard
from app.utils import is_uuid


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
    print(f"user_context: {user_contexts}")
    if isinstance(event, types.message.Message):
        # отримати отсортований за lastdate список всіх статусів користувача (GET user_contexts/)
        # формуємо список кнопок для клавіатури, створюємо клавіатуру (personal.keyboards.CombiKeyboardGenerator).
        print(f"event is Message, message_id: {event.message_id}")
        scrollkey_buttons = [
            [
                InlineKeyboardButton(
                    text=user_context["context_1"]["name"]
                    + "-"
                    + user_context["context_2"]["name"],
                    callback_data=str(user_context["id"]),
                )
            ]
            for user_context in user_contexts
        ]
        additional_buttons = [
            [
                InlineKeyboardButton(
                    text="set as current context", callback_data="#SET_CURRENT_CONTEXT"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="create new context", callback_data="#CREATE_NEW_CONTEXT"
                )
            ],
            [
                InlineKeyboardButton(
                    text="send to arhive", callback_data="#SEND_TO_ARCHIVE"
                ),
                InlineKeyboardButton(
                    text="extract from archive", callback_data="#EXTRACT_FROM_ARCHIVE"
                ),
            ],
        ]
        kb = CombiKeyboardGenerator(
            scrollkeys=scrollkey_buttons,
            additional_buttons_list=additional_buttons,
            max_rows_number=5,
            scroll_step=1,
        )
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
        await event.answer(
            user_contexts[0]["context_1"]["name"]
            + "-"
            + user_contexts[0]["context_2"]["name"],
            reply_markup=tmp_storage[key].markup(),
        )
    if isinstance(event, types.CallbackQuery):
        # дивимось на callback.data, в залежності від нього:
        # або (обрана дія перебачає нову клавіатуру в новому стані)
        #    - видаляємо з глобального обїекта існуючу клавіатуру
        #    - визиваємо відповідний обробник
        # або (скрол клавіатурі)
        #     - змінюємо стан клавіатури в глобальному сховищі
        #     - корегуємо повідомлення з новою клавіатурою
        if event.data == "#CREATE_NEW_CONTEXT":
            pass
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
    dp.callback_query.register(cmd_settings, StateFilter(UserSettings))
