from typing import Optional
from uuid import UUID

from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from app.base_functions.translator import get_translate
from app.db_functions.personal import get_context_id_db, get_help_db, add_help_db
from app.handlers.personal.bot_commands import bot_commands
from app.scheme.transdata import TranslateRequest


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
    user_language: UUID = await get_context_id_db(msg.from_user.language_code.split("-")[0])  # type: ignore
    # status = CURRENT, language = USER'S
    help_text: Optional[str] = await get_help_db(state_name, user_language)

    if help_text is None:
        # status = CURRENT, language = ENGLISH
        en_help_text: Optional[str] = await get_help_db(
            state_name, id_en_context := await get_context_id_db("en")
        )
        if en_help_text is None:
            state_name = "None"
            # status = NONE, language = USER'S
            help_text = await get_help_db(state_name, user_language)
            if help_text is None:
                # status = NONE, language = ENGLISH
                en_help_text = await get_help_db(state_name, id_en_context)
                help_text: str = get_translate(  # type: ignore
                    TranslateRequest(
                        native_lang=user_language, foreign_lang="en", line=en_help_text
                    )
                ).translated_text
                await add_help_db(state=state_name, help_text=help_text, language=user_language)  # type: ignore
        else:
            help_text: str = get_translate(  # type: ignore
                TranslateRequest(
                    native_lang=user_language, foreign_lang="en", line=en_help_text
                )
            ).translated_text
            await add_help_db(state=state_name, help_text=help_text, language=user_language)  # type: ignore

    commands: dict = {f"_{str(i[2])}": f"/{i[0]}" for i in bot_commands}
    return await msg.answer(help_text.format(**commands))  # type: ignore


def register_handler_help(dp: Dispatcher) -> None:
    dp.message.register(cmd_help, Command(commands=["help"]))
