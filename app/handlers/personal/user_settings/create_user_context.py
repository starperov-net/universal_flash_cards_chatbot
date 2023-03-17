from uuid import UUID
from aiogram import types, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from app.handlers.personal.user_settings.user_settings import UserSettings
from app.create_bot import bot
from app.db_functions.personal import get_context
from app.storages import TmpStorage
from app.tables import ContextClass
from app.handlers.personal.keyboards import (
    KeyKeyboard,
    KeyboardCreateUserContext,
)
from app.base_functions.utils import match_to_uuid4


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
        scrollkey_buttons = [
            [
                InlineKeyboardButton(
                    text=f"{context['name']} ({context['name_alfa2'].upper()})",
                    callback_data=str(context["id"]),
                )
            ]
            for context in contexts
        ]
        additional_buttons = [
            [
                InlineKeyboardButton(text="DONE!", callback_data="#DONE!"),
            ],
        ]
        pre_additional_buttons = [
            [
                InlineKeyboardButton(
                    text="set the first language", callback_data="#SET_FIRST_LNG"
                ),
                InlineKeyboardButton(
                    text="set the second language", callback_data="#SET_SECOND_LNG"
                ),
            ]
        ]
        kb = KeyboardCreateUserContext(
            scrollkeys=scrollkey_buttons,
            additional_buttons_list=additional_buttons,
            pre_additional_buttons_list=pre_additional_buttons,
            max_rows_number=10,
            scroll_step=7,
        )
        tmp_storage[key] = kb
    elif callback.data == "#DONE!":
        print("in #DONE! branch")
        print(f"tmp_storage[key]: {tmp_storage[key]}")
        await tmp_storage[key].set_user_context(callback.from_user.id)
        await callback.message.edit_text(text=tmp_storage[key].text, parse_mode="HTML")
        await state.clear()
        return
    elif callback.data == "#DOWN":
        tmp_storage[key].markup_down()
    elif callback.data == "#UP":
        tmp_storage[key].markup_up()
    elif callback.data == "#SET_SECOND_LNG":
        await tmp_storage[key].set_second()
    elif callback.data == "#SET_FIRST_LNG":
        await tmp_storage[key].set_first()
    elif callback.data and match_to_uuid4(callback.data):
        id_ctx = UUID(callback.data)
        await tmp_storage[key].set_lng(id_ctx)

    await callback.message.edit_text(
        text=tmp_storage[key].text,
        reply_markup=tmp_storage[key].markup(),
        parse_mode="HTML",
    )


def register_handler_create_user_context(dp: Dispatcher) -> None:
    """
    It should work under the condition:
    - CallbackQuery and state from UserSettings.create_new_user_context
    (priority lower than for command /help, /cancel)
    """
    dp.callback_query.register(
        create_user_context, StateFilter(UserSettings.create_new_user_context)
    )
