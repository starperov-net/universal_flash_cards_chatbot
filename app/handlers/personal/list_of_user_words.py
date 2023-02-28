from aiogram.filters import Command

from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext

from app.base_functions.list_of_words import get_list_of_words


async def list_of_user_words(msg: types.Message, state: FSMContext) -> None:
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

    list_of_words = await get_list_of_words(msg.from_user.id)
    for card in list_of_words:
        await msg.answer(text=f"{card['foreign_word']}    {card['native_word']}    {card['learning_status']}")



def register_handler_list(dp: Dispatcher) -> None:
    """A handler's registrator.

    Parameters:
        dp:
            see base class

    Returns:
        None
    """

    dp.message.register(
        list_of_user_words, Command(commands=["mywords", "список моїх слів", "список моих слов"])
    )
