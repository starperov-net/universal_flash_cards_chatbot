from typing import List
from aiogram.filters import Command

from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext

from app.base_functions.list_of_words import get_list_of_words


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

    list_of_words: List[dict] = await get_list_of_words(msg.from_user.id)
    # this loop is temporary
    for card in list_of_words:
        await msg.answer(
            text=f"{card['foreign_word']}    {card['native_word']}    {card['learning_status']}"
        )
    # this return is temporary
    return await msg.answer(text="It's all")


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
