"""Handles 'mywords' mode.

Using the /mywords command will display a 10 button scrolling keyboard.
One or two auxiliary buttons (DOWN, UP), others contain information about one user's card:
<word_in_target_language: word_in_native_language 👉 learning_status>.
By clicking on the button with information about the card, under the button
a context menu will appear in the form of a keyboard with two buttons: DELETE and BACK TO LIST.
When the context menu appears, all other buttons with information about the cards disappear
and reappear after pressing the BACK TO LIST button.
DELETE button - deletes the card.
State here is just like storage.
"""
from typing import Optional, Union
from uuid import UUID

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext

from app.base_functions.list_of_words import get_list_of_words
from app.handlers.personal.callback_data_states import MyWordCallbackData
from app.handlers.personal.keyboards import (
    create_set_of_buttons_with_user_words,
    MyWordsScrollKeyboardGenerator,
)
from app.states.states import FSMMyWords


async def show_my_words(msg: types.Message, state: FSMContext) -> types.Message:
    """A handler to start <myWords> mode.

    Getting list of user words mode with </myWords> command.

    Parameters:
        msg: types.Message
        state: State Machine

    Returns:
        Message. See base class
    """
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    list_of_words: list[dict] = await get_list_of_words(msg.from_user.id)
    combi_keyboard_generator: MyWordsScrollKeyboardGenerator = (
        MyWordsScrollKeyboardGenerator(
            scrollkeys=create_set_of_buttons_with_user_words(list_of_words),
            max_rows_number=10,
        )
    )

    await state.set_state(FSMMyWords.mywords)
    await state.set_data({"combi_keyboard_generator": combi_keyboard_generator})

    return await msg.answer(
        text=f"You have {len(list_of_words)} words.",
        reply_markup=combi_keyboard_generator.markup(),
    )


async def my_words_down(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Union[types.Message, bool]:
    """Handler to push DOWN-button in the scroll keyboard in <myWords> mode.

    Parameters:
        callback_query: see base class
        state: State Machine
    """
    state_data: dict = await state.get_data()
    combi_keyboard_generator: Optional[MyWordsScrollKeyboardGenerator] = state_data.get(
        "combi_keyboard_generator"
    )

    if combi_keyboard_generator is None:
        return await callback_query.answer(
            "Update the wordlist by calling the /mywords command."
        )
    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    return await callback_query.message.edit_reply_markup(
        reply_markup=combi_keyboard_generator.markup_down()
    )


async def my_words_up(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Union[types.Message, bool]:
    """Handler to push UP-button in the scroll keyboard in <myWords> mode.

    Parameters:
        callback_query: see base class
        state: State Machine
    """
    state_data: dict = await state.get_data()
    combi_keyboard_generator: Optional[MyWordsScrollKeyboardGenerator] = state_data.get(
        "combi_keyboard_generator"
    )

    if combi_keyboard_generator is None:
        return await callback_query.answer(
            "Update the wordlist by calling the /mywords command"
        )
    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    return await callback_query.message.edit_reply_markup(
        reply_markup=state_data["combi_keyboard_generator"].markup_up()
    )


async def context_menu_for_one_myword(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    callback_data: MyWordCallbackData,
) -> Union[types.Message, bool]:
    """Handler to push button with card info in the scroll keyboard in <myWords> mode.

    Parameters:
        callback_query: see base class
        state: State Machine
        callback_data: FSM storage
    """
    state_data: dict = await state.get_data()
    card_id: UUID = callback_data.card_id
    combi_keyboard_generator: Optional[MyWordsScrollKeyboardGenerator] = state_data.get(
        "combi_keyboard_generator"
    )

    if combi_keyboard_generator is None:
        return await callback_query.answer(
            "Update the wordlist by calling the /mywords command"
        )
    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    try:
        return await callback_query.message.edit_reply_markup(
            reply_markup=combi_keyboard_generator.build_context_menu_for_one_word(
                card_id
            )
        )
    # when the message is not modified
    except TelegramBadRequest:
        return await callback_query.answer(
            "Select the 'DELETE' or 'BACK TO LIST' button."
        )


async def cancel_context_menu_for_one_myword(
    callback_query: types.CallbackQuery, state: FSMContext
) -> Union[types.Message, bool]:
    """Handler to push BACK TO LIST button in the scroll keyboard in <myWords> mode.

    Returns to the user's wordlist.

        Parameters:
            callback_query: see base class
            state: State Machine
    """
    state_data: dict = await state.get_data()
    combi_keyboard_generator: Optional[MyWordsScrollKeyboardGenerator] = state_data.get(
        "combi_keyboard_generator"
    )

    if combi_keyboard_generator is None:
        return await callback_query.answer(
            "Update the wordlist by calling the /mywords command"
        )
    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    return await callback_query.message.edit_reply_markup(
        reply_markup=combi_keyboard_generator.markup()
    )


def register_handler_mywords(dp: Dispatcher) -> None:
    """A handler's registrator.

    Parameters:
        dp:
            see base class

    Returns:
        None
    """

    dp.message.register(
        show_my_words,
        Command(commands=["mywords", "список моїх слів", "список моих слов"]),
    )
    dp.callback_query.register(my_words_down, F.data == "#DOWN")
    dp.callback_query.register(my_words_up, F.data == "#UP")
    dp.callback_query.register(context_menu_for_one_myword, MyWordCallbackData.filter())
    dp.callback_query.register(
        cancel_context_menu_for_one_myword, F.data == "#BACK TO LIST"
    )
