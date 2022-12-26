from typing import Optional

from aiogram import Dispatcher, F, types, filters
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.handlers.personal.keyboards as kb
from app.base_functions.translator import get_translate
from app.db_functions.personal import (add_user_context_db, add_user_db,
                                       get_or_create_item_db,
                                       get_user_context_db, get_user_db,
                                       add_item_relation_db, get_context_id_db,
                                       get_translated_text_db)

from app.scheme.transdata import ISO639_1, TranslateRequest, TranslateResponse
from app.tables import User, UserContext
from app.tests.utils import TELEGRAM_USER_GOOGLE


class FSMChooseLanguage(StatesGroup):
    native_language = State()
    target_language = State()


async def start(msg: types.Message, state: FSMContext) -> None:
    await greeting(msg)
    await get_user_data(msg, state)


async def greeting(msg: types.Message) -> None:
    await msg.answer(text=f"Hello, {msg.from_user.full_name}")


async def get_user_data(msg: types.Message, state: FSMContext) -> None:
    user_context_db: Optional[UserContext] = await get_user_context_db(msg.from_user.id)

    if user_context_db:
        await msg.answer(
            text=f"{user_context_db.user.first_name}, "
                 f"your native language is {user_context_db.context_1.name}, "
                 f"your target - {user_context_db.context_2.name}",
        )
        return

    await state.set_state(FSMChooseLanguage.native_language)
    await msg.answer(
        text="what is your native language?", reply_markup=kb.select_language_keyboard
    )


async def select_native_language(
        callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    await state.set_data({"native_lang": callback_query.data})
    await state.set_state(FSMChooseLanguage.target_language)
    await callback_query.message.answer(
        text="what is your target language?",
        reply_markup=kb.select_language_keyboard,
    )


async def select_target_language(
        callback_query: types.CallbackQuery, state: FSMContext
) -> None:
    await state.update_data({"target_lang": callback_query.data})
    user_db = await get_user_db(callback_query.from_user.id)
    if user_db is None:
        user_db: Optional[User] = await add_user_db(callback_query.from_user)

    state_data = await state.get_data()
    user_context_db = await add_user_context_db(state_data, user_db)

    await callback_query.message.answer(
        text=f"{user_db.first_name}, "
             f"your native language is {user_context_db.context_1.name}, "
             f"your target - {user_context_db.context_2.name}",
    )
    await state.clear()


async def translate_text(msg: types.Message):
    user_context: UserContext = await get_user_context_db(msg.from_user.id)
    translated_word: Optional[str] = await get_translated_text_db(
        msg.text,
        msg.from_user.id,
        user_context.context_1.id,
        user_context.context_2.id
    )

    if translated_word is None:

        request = TranslateRequest(
            native_lang=user_context.context_1.name_alfa2,
            foreign_lang=user_context.context_2.name_alfa2,
            line=msg.text,
        )

        try:
            translate: TranslateResponse = get_translate(input_=request)

        except ValueError as er:
            await msg.answer(er.args[0])

        else:

            input_text_context_id = await get_context_id_db(translate.input_text_language)
            translated_text_context_id = await get_context_id_db(translate.translated_text_language)

            item_1 = await get_or_create_item_db(translate.input_text, input_text_context_id, user_context.user.id)
            item_2 = await get_or_create_item_db(translate.translated_text, translated_text_context_id,
                                                 user_context.user.id)
            google = await get_user_db(TELEGRAM_USER_GOOGLE.id)
            await add_item_relation_db(google.id, item_1, item_2)

        await msg.answer(f'you wrote {msg.text}. Translated - "{translated_word}"')

def register_handler_start(dp: Dispatcher):
    dp.message.register(start, Command(commands=["start", "початок"]))
    dp.message.register(greeting, Command(commands=["hello"]))
    dp.callback_query.register(
        select_native_language, FSMChooseLanguage.native_language
    )
    dp.callback_query.register(
        select_target_language, FSMChooseLanguage.target_language
    )
    dp.message.register(translate_text)  # F.test.regexp("[a-zA-Z ]"))
