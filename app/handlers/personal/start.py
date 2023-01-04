from typing import Optional
from uuid import UUID

from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.handlers.personal.keyboards as kb
from app.base_functions.translator import get_translate
from app.db_functions.personal import (
    add_user_context_db,
    add_user_db,
    get_or_create_item_db,
    get_user_context_db,
    get_user_db,
    add_item_relation_db,
    get_context_id_db,
    get_translated_text_from_item_relation,
    add_card_db,
    get_item_relation_by_text_db,
    is_words_in_card_db,
)
from app.handlers.personal.callback_data_states import ToStudyCallbackData

from app.scheme.transdata import TranslateRequest, TranslateResponse
from app.tables import User, UserContext, Item, ItemRelation
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


async def google_translate(user_context, text) -> [ItemRelation | ValueError]:
    """
    Exception ValueError raise when language of the inputted word
    is not in [user_context.context_1, user_context.context_2]
    """
    request = TranslateRequest(
        native_lang=user_context.context_1.name_alfa2,
        foreign_lang=user_context.context_2.name_alfa2,
        line=text,
    )

    try:
        translate: TranslateResponse = get_translate(input_=request)
    except ValueError:
        raise

    else:

        input_text_context_id: UUID = await get_context_id_db(
            translate.input_text_language
        )
        translated_text_context_id: UUID = await get_context_id_db(
            translate.translated_text_language
        )

        item_1: Item = await get_or_create_item_db(
            translate.input_text, input_text_context_id, user_context.user.id
        )
        item_2: Item = await get_or_create_item_db(
            translate.translated_text, translated_text_context_id, user_context.user.id
        )
        google: User = await get_user_db(TELEGRAM_USER_GOOGLE.id)
        item_relation: ItemRelation = await add_item_relation_db(
            google.id, item_1, item_2
        )

        return item_relation


async def translate_text(msg: types.Message) -> types.Message:
    """
    1.received text for translation converts to lowercase.
    2.getting translate from our own database.
      return item_relation
    3.if we don't have an item_relation, using google_translate
      in this case save this text and translates_text as items and item_relation
      return item_relation
    4.shows the translated text and offers to choose 'add to study'/'my variant'/'nothing to do'.
      If the language of the entered word is not in [user_context.context_1, user_context.context_2]
      raises an Exception ValueError and shows the translation, but indicating from
      which language the translation was made.
    """
    user_context: UserContext = await get_user_context_db(msg.from_user.id)
    inputted_text_lowercase: str = msg.text.strip().lower()
    item_relation: Optional[ItemRelation] = await get_item_relation_by_text_db(
        inputted_text_lowercase,
        msg.from_user.id,
        user_context.context_1.id,
        user_context.context_2.id,
    )
    if not item_relation:
        try:
            item_relation: ItemRelation = await google_translate(
                user_context, inputted_text_lowercase
            )
        except ValueError as er:
            return await msg.answer(er.args[0])

    translated_text: str = get_translated_text_from_item_relation(
        inputted_text_lowercase, item_relation
    )
    return await msg.answer(
        translated_text, reply_markup=kb.what_to_do_with_text_keyboard(item_relation.id)
    )


async def add_words_to_study(
    callback_query: types.CallbackQuery, callback_data: ToStudyCallbackData
):
    """
    Creates an in 'card'.
    Before doing this, check if the user already has a pair of such words in the item_relation (with point context)
    to study. If the couple is already in the "card", then it informs about it.
    """
    is_words_in_card: bool = await is_words_in_card_db(
        callback_query.from_user.id, callback_data.item_relation_id
    )
    if is_words_in_card:
        await callback_query.answer("Already under study!")
    else:
        await add_card_db(callback_query.from_user.id, callback_data.item_relation_id)
        await callback_query.answer("Added to study.")


async def my_variant(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer("it is example")


async def nothing_to_do(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer("nothing_to_do")


def register_handler_start(dp: Dispatcher):
    dp.message.register(start, Command(commands=["start", "початок"]))
    dp.message.register(greeting, Command(commands=["hello"]))
    dp.callback_query.register(
        select_native_language, FSMChooseLanguage.native_language
    )
    dp.callback_query.register(
        select_target_language, FSMChooseLanguage.target_language
    )
    dp.callback_query.register(add_words_to_study, ToStudyCallbackData.filter())
    dp.callback_query.register(my_variant, F.data == "my_variant")
    dp.callback_query.register(nothing_to_do, F.data == "nothing_to_do")
    dp.message.register(translate_text)  # F.test.regexp("[a-zA-Z ]"))
