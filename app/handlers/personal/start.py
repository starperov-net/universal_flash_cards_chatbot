from typing import Any, Optional, Union
from uuid import UUID

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.handlers.personal.keyboards as kb
from app.base_functions.translator import get_translate
from app.db_functions.personal import (
    add_card_db,
    add_item_relation_db,
    add_user_context_db,
    get_context_id_db,
    get_existing_user_id_db,
    get_item_relation_by_text_db,
    get_item_relation_with_related_items_by_id_db,
    get_or_create_item_db,
    get_or_create_user_db,
    get_translated_text_from_item_relation,
    get_user_context_db,
    is_words_in_card_db,
    get_or_create_item_by_text_and_usercontext_db,
    get_or_create_item_relation_db,
)
from app.handlers.personal.callback_data_states import (
    ToStudyCallbackData,
    CustomTranslationCallbackData,
)
from app.scheme.transdata import TranslateRequest, TranslateResponse
from app.states.states import (
    FSMChooseLanguage,
    FSMCustomTranslation,
)
from app.tables import ItemRelation, User, UserContext, Item
from app.tests.utils import TELEGRAM_USER_GOOGLE


async def start(msg: types.Message, state: FSMContext) -> None:
    await greeting(msg)
    await get_user_data(msg, state)


async def greeting(msg: types.Message) -> types.Message:
    # from_user is None if messages sent to channels
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    return await msg.answer(text=f"Hello, {msg.from_user.full_name}")


async def get_user_data(msg: types.Message, state: FSMContext) -> types.Message:
    # from_user is None if messages sent to channels
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    user_context_db: Optional[UserContext] = await get_user_context_db(msg.from_user.id)
    if user_context_db:
        return await msg.answer(
            text=f"{user_context_db.user.first_name}, "
            f"your native language is {user_context_db.context_1.name}, "
            f"your target - {user_context_db.context_2.name}",
        )

    await state.set_state(FSMChooseLanguage.native_language)
    return await msg.answer(
        text="what is your native language?", reply_markup=kb.select_language_keyboard
    )


async def select_native_language(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Union[types.Message, bool]:
    # message is None if the message is too old
    if callback_query.message is None:
        return await callback_query.answer("Message is None if the message is too old")

    await state.set_data({"native_lang": callback_query.data})
    await state.set_state(FSMChooseLanguage.target_language)
    return await callback_query.message.answer(
        text="what is your target language?",
        reply_markup=kb.select_language_keyboard,
    )


async def select_target_language(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Union[types.Message, bool]:
    # message is None if the message is too old
    if callback_query.message is None:
        return await callback_query.answer("Message is None if the message is too old")

    await state.update_data({"target_lang": callback_query.data})
    user_db: User = await get_or_create_user_db(callback_query.from_user)

    state_data: dict[str, Any] = await state.get_data()
    user_context_db = await add_user_context_db(state_data, user_db)
    await state.clear()

    return await callback_query.message.answer(
        text=f"{user_db.first_name}, "
        f"your native language is {user_context_db.context_1.name}, "
        f"your target - {user_context_db.context_2.name}",
    )


async def google_translate(user_context: UserContext, text: str) -> ItemRelation:
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
        item_1: UUID = await get_or_create_item_db(
            translate.input_text, input_text_context_id, user_context.user.id
        )
        item_2: UUID = await get_or_create_item_db(
            translate.translated_text, translated_text_context_id, user_context.user.id
        )
        google: UUID = await get_existing_user_id_db(TELEGRAM_USER_GOOGLE.id)
        item_relation_id: UUID = await add_item_relation_db(google, item_1, item_2)
        item_relation_with_related_items: ItemRelation = (
            await get_item_relation_with_related_items_by_id_db(item_relation_id)
        )

        return item_relation_with_related_items


async def translate_text(msg: types.Message) -> types.Message:
    """
    1.received text for translation converts to lowercase.
    2.getting translate from our own database.
      return item_relation
    3.if we don't have an item_relation, using google_translate
      in this case save this text and translates_text as items and item_relation
      return item_relation
    4.shows the translated text and offers to choose 'add to study'/'my variant'.
      If the language of the entered word is not in [user_context.context_1, user_context.context_2]
      raises an Exception ValueError and shows the translation, but indicating from
      which language the translation was made.
    """
    # from_user is None if messages sent to channels
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")
    # For text messages, the actual UTF-8 text of the message
    if msg.text is None:
        return await msg.answer("Only text can be entered")

    user_context: Optional[UserContext] = await get_user_context_db(msg.from_user.id)
    if user_context is None:
        return await msg.answer("To work with bot use /start command")

    inputted_text_lowercase: str = msg.text.strip().lower()

    try:
        # if item_relation doesn't exist in the database, a new item_relation is created using google_translate()
        item_relation: ItemRelation = await get_item_relation_by_text_db(
            inputted_text_lowercase, user_context
        ) or await google_translate(user_context, inputted_text_lowercase)
    except ValueError as er:
        return await msg.answer(er.args[0])

    translated_text: str = await get_translated_text_from_item_relation(
        inputted_text_lowercase, item_relation
    )
    return await msg.answer(
        translated_text,
        reply_markup=kb.what_to_do_with_text_keyboard(
            item_relation.id, inputted_text_lowercase
        ),
    )


async def add_words_to_study(
    callback_query: types.CallbackQuery, callback_data: ToStudyCallbackData
) -> None:
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


async def my_variant(
    callback_query: types.CallbackQuery,
    callback_data: CustomTranslationCallbackData,
    state: FSMContext,
) -> None:
    """Button click handler <my_variant>.

    Parameters:
        callback_query:
            see base class
        callback_data:
            see base class
        state:
            State Machine where save data current session:
                {"incoming_word": "airplane"}
    Return:
        None
    """

    data_for_fsm: dict[str, Any] = {"incoming_word": callback_data.text}

    await callback_query.message.answer(  # type: ignore
        text="Enter your custom translation into the message field, please."
    )

    await state.set_state(FSMCustomTranslation.custom_translation)
    await state.set_data(data_for_fsm)


async def get_custom_translation(
    msg: types.Message, state: FSMContext
) -> types.Message:
    """Handler to process a word translated by user.

    Parameters:
        msg:
            see base class
        state:
            State Machine where save data current session:
                {"incoming_word": "airplane"}
    Return:
        msg:
            see base class
    """

    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")
    if msg.text is None:
        return await msg.answer("Only text can be entered")

    state_data: dict[str, Any] = await state.get_data()

    inputted_text_lowercase = state_data["incoming_word"]
    user_personal_translation_original_case: str = msg.text.strip()

    user_context: Optional[UserContext] = await get_user_context_db(msg.from_user.id)
    if user_context is None:
        return await msg.answer("To work with bot use /start command")

    item_1: Optional[Item] = await get_or_create_item_by_text_and_usercontext_db(
        inputted_text_lowercase, user_context
    )
    if not item_1:
        await state.clear()
        return await msg.answer("😭😭😭😭😭")

    input_text_context_id: UUID = item_1.context

    translated_text_context_id: UUID = list(
        set((user_context.context_1.id, user_context.context_2.id))
        - set((input_text_context_id,))
    )[0]

    item_2: UUID = await get_or_create_item_db(
        user_personal_translation_original_case,
        translated_text_context_id,
        user_context.user.id,
    )

    item_relation_id: UUID = await get_or_create_item_relation_db(
        user_context.user.id, item_1.id, item_2
    )
    is_words_in_card: bool = await is_words_in_card_db(
        msg.from_user.id, item_relation_id
    )
    if is_words_in_card:
        await state.clear()
        return await msg.answer("You have this pair of words in your words database!")
    else:
        await add_card_db(msg.from_user.id, item_relation_id)
        await state.clear()
        return await msg.answer(
            f"You entered - {inputted_text_lowercase} - to get translation.\n"
            f"You pick - {user_personal_translation_original_case} - as your custom translation.\n\n"
            "Added to study."
        )


def register_handler_start(dp: Dispatcher) -> None:
    dp.message.register(start, Command(commands=["start", "початок"]))
    dp.message.register(greeting, Command(commands=["hello"]))
    dp.callback_query.register(
        select_native_language, FSMChooseLanguage.native_language
    )
    dp.callback_query.register(
        select_target_language, FSMChooseLanguage.target_language
    )
    dp.callback_query.register(add_words_to_study, ToStudyCallbackData.filter())
    dp.callback_query.register(my_variant, CustomTranslationCallbackData.filter())
    dp.message.register(get_custom_translation, FSMCustomTranslation.custom_translation)
    dp.message.register(translate_text)  # F.test.regexp("[a-zA-Z ]"))
