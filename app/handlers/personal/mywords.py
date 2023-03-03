from aiogram.filters import Command

from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext

from app.base_functions.list_of_words import get_list_of_words
from app.handlers.personal.keyboards import create_scrollkeys_for_mywords, ScrollKeyboardGenerator
from app.states.states import FSMMyWords


async def show_my_words(msg: types.Message, state: FSMContext) -> types.Message:
    """A handler to start <myWords> mode.

    Getting list of user words mode with </myWords> command.

    Parameters:
        msg: types.Message

        state:
            State Machine

    Returns:
        list_of_words:
            list[dict]

    """
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    list_of_words: list[dict] = await get_list_of_words(msg.from_user.id)
    combi_keyboard_generator: ScrollKeyboardGenerator = ScrollKeyboardGenerator(
        scrollkeys=create_scrollkeys_for_mywords(list_of_words),
        max_rows_number=10
    )

    await state.set_state(FSMMyWords.mywords)
    await state.set_data({"combi_keyboard_generator": combi_keyboard_generator})

    await msg.answer(
        text=f"You have {len(list_of_words)} words.",
        reply_markup=combi_keyboard_generator.markup()
        )


async def my_words_down(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    state_data: dict = await state.get_data()
    if callback_query.message is None:
        await callback_query.answer("Pay attention the message is too old.")
    else:
        await callback_query.message.edit_reply_markup(
            reply_markup=state_data["combi_keyboard_generator"].markup_down()
        )


async def my_words_up(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    state_data: dict = await state.get_data()
    if callback_query.message is None:
        await callback_query.answer("Pay attention the message is too old.")
    else:
        await callback_query.message.edit_reply_markup(
            reply_markup=state_data["combi_keyboard_generator"].markup_up()
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
