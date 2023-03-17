from typing import Optional
from uuid import UUID

from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from app.base_functions.translator import get_translation_from_string_with_paragraph
from app.db_functions.personal import get_context_id_db, get_help_db, add_help_db
from app.handlers.personal.bot_commands import bot_commands


async def cmd_help(msg: types.Message, state: FSMContext) -> types.Message:
    """Gives a hint to the user depending on what stage (state) he is at.

    For each state of the bot (FSM) displays a specific hint
    in the language of the user's telegram interface.
    If the help table does not have a row with the current state,
    it will return a help message with the status "None".

    Parameters:
        msg: types.Message
        state: State Machine
    """
    state_name: str = str(await state.get_state())
    user_language: str = msg.from_user.language_code.split("-")[0]  # type: ignore
    user_language_id: UUID = await get_context_id_db(user_language)
    # status = CURRENT, language = USER'S
    help_text: Optional[str] = await get_help_db(state_name, user_language_id)

    if help_text is None:
        # status = CURRENT, language = ENGLISH
        en_help_text: Optional[str] = await get_help_db(
            state_name, id_en_context := await get_context_id_db("en")
        )
        if en_help_text is None:
            state_name = "None"
            # status = NONE, language = USER'S
            help_text = await get_help_db(state_name, user_language_id)
            if help_text is None:
                # status = NONE, language = ENGLISH
                en_help_text = await get_help_db(state_name, id_en_context)
                help_text: str = get_translation_from_string_with_paragraph(  # type: ignore
                    text=en_help_text,  # type: ignore
                    target_language=user_language,
                    source_language="en",
                )
                await add_help_db(state=state_name, help_text=help_text, language=user_language_id)  # type: ignore
        else:
            help_text: str = get_translation_from_string_with_paragraph(  # type: ignore
                text=en_help_text, target_language=user_language, source_language="en"
            )
            await add_help_db(state=state_name, help_text=help_text, language=user_language_id)  # type: ignore

    commands: dict = {f"_{str(i[2])}": f"/{i[0]}" for i in bot_commands}
    return await msg.answer(help_text.format(**commands), parse_mode="HTML")  # type: ignore


def register_handler_help(dp: Dispatcher) -> None:
    dp.message.register(cmd_help, Command(commands=["help"]))
