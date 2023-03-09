from typing import Optional
from uuid import UUID

from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.base_functions.translator import get_translate
from app.db_functions.personal import get_context_id_db, get_help_db, add_help_db
from app.handlers.personal.bot_commands import bot_commands
from app.scheme.transdata import TranslateRequest


async def cmd_help(msg: types.Message, state: FSMContext) -> None:
    """Gives a hint to the user depending on what stage (state) he is at.

    For each state of the bot () displays a specific hint in the language
    of the user's telegram interface.

    Parameters:
        msg: types.Message
        state: State Machine
    """
    state_name: str = str(await state.get_state())
    telegram_language: UUID = await get_context_id_db(msg.from_user.language_code.split("-")[0])  # type: ignore
    text: Optional[str] = await get_help_db(state_name, telegram_language)

    if text is None:
        # if help with context 'en' does not exist, help_text will get and save as in state 'None'
        en_text = await get_help_db(
            state_name, id_en_context := await get_context_id_db("en")
        ) or await get_help_db("None", id_en_context)
        text: str = get_translate(  # type: ignore
            TranslateRequest(
                native_lang=telegram_language, foreign_lang="en", line=en_text
            )
        ).translated_text
        await add_help_db(state=state_name, help_text=text, language=telegram_language)  # type: ignore

    await msg.answer(add_commands_to_text(text))  # type: ignore


def add_commands_to_text(text: str) -> str:
    """Completes the text of the answer message for the /help command by adding commands.

    To format a string by indexes, the order of the indexes must be observed:
    the index specified in the text must match the command index in the list of commands (bot_commands).

    Parameters:
        text: text of the answer message for the /help command without commands
    Return:
        Formatted text.
    """
    sorted_cmds: list[tuple[str, str, int]] = sorted(bot_commands, key=lambda x: x[2])
    formatted_list_of_cmds: list[Optional[str]] = []

    # len(bot_commands) should be equal to max command number, so missing indexes need to be filled in (by None)
    if len(bot_commands) == sorted_cmds[-1][2]:
        formatted_list_of_cmds = ["/" + cmd[0] for cmd in sorted_cmds]
    else:
        count_none = 0
        for index, cmd_data in enumerate(sorted_cmds):
            if cmd_data[2] != index + count_none:
                while cmd_data[2] > index + count_none:
                    formatted_list_of_cmds.append(None)
                    count_none += 1
            formatted_list_of_cmds.append("/" + cmd_data[0])

    return text.format(*formatted_list_of_cmds)


def register_handler_help(dp: Dispatcher) -> None:
    dp.message.register(cmd_help, Command(commands=["help"]))
