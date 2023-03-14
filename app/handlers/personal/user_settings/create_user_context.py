from uuid import UUID
from aiogram import types, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.db_functions.personal import get_context, get_default_language
from app.storages import TmpStorage
from app.tables import ContextClass
from app.handlers.personal.keyboards import (
    KeyKeyboard,
    KeyboardCreateUserContext,
)


def get_current_context_class_id(name: str) -> UUID:
    """This is a "crutch" that is needed to get the ID for the class context
    (since different databases and, accordingly, different IDs are used during
    development and real work). Used as a constant later in the create_user_context module"""
    row = (
        ContextClass.select()
        .where(ContextClass.name.like(f"%{name}%"))
        .first()
        .run_sync()
    )
    return row["id"]


CONTEXT_CLASS_LANGUAGE_ID = get_current_context_class_id("language")
print(f"CONTEXT_CLASS_LANGUAGE_ID: {CONTEXT_CLASS_LANGUAGE_ID}")


async def create_user_context(
    callback: types.CallbackQuery, state: FSMContext, tmp_storage: TmpStorage
) -> None:
    print("in create_user_context".center(120, "-"))
    await state.set_state(UserSettings.create_new_user_context)
    print(f"input callback.data: {callback.data}")
    print(f"set state: {await state.get_state()}")
    default_lang = await get_default_language(callback.from_user)
    print(f"default_lang: {default_lang}")
    key = KeyKeyboard(
        bot_id=bot.id,
        chat_id=callback.chat_instance,
        user_id=callback.from_user.id,
        message_id=callback.message.message_id if callback.message else None,
    )
    contexts = await get_context(context_class_id=CONTEXT_CLASS_LANGUAGE_ID)
    kb = tmp_storage.get(key)
    if not kb:
        # create starting kb for create user context
        data = [None, None, False]
        scrollkey_buttons = [
            [
                InlineKeyboardButton(
                    text=f"{context['name']} ({context['name_alfa2']})",
                    callback_data=str(context["id"]),
                )
            ]
            for context in contexts
        ]
        additional_buttons = [
            [
                InlineKeyboardButton(text="TEST", callback_data="#TEST"),
            ],
        ]
        kb = KeyboardCreateUserContext(
            scrollkeys=scrollkey_buttons,
            additional_buttons_list=additional_buttons,
            max_rows_number=10,
            scroll_step=1,
            data=data,
        )

    tmp_storage[key] = kb
    await callback.message.answer(
        text=kb.text, reply_markup=kb.markup(), parse_mode="HTML"
    )


def register_handler_create_user_context(dp: Dispatcher) -> None:
    """
    Повинно спрацьовувати при умові:
    - CallbackQuery і стан з UserSettings.create_new_user_context (пріоритет нижче ніж для команди /help, /cancel)
    """
    dp.callback_query.register(
        create_user_context, StateFilter(UserSettings.create_new_user_context)
    )
