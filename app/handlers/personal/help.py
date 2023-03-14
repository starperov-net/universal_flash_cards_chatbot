from typing import Optional
from uuid import UUID

import jinja2
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from jinja2 import Environment
from jinja2.environment import Template


from app.base_functions.translator import get_translate
from app.db_functions.personal import get_context_id_db, get_help_db, add_help_db
from app.handlers.personal.bot_commands import bot_commands
from app.scheme.transdata import TranslateRequest


async def cmd_help(msg: types.Message, state: FSMContext) -> None:
    """Gives a hint to the user depending on what stage (state) he is at.

    For each state of the bot (FSM) displays a specific hint in the language
    of the user's telegram interface.

    Parameters:
        msg: types.Message
        state: State Machine
    """
    state_name: str = str(await state.get_state())
    telegram_language: UUID = await get_context_id_db(msg.from_user.language_code.split("-")[0])  # type: ignore
    text: Optional[str] = await get_help_db(state_name, telegram_language)

    if text is None:
        # if help with context 'en' does not exist, help_text will get help_text by state 'None'
        en_text: Optional[str] = await get_help_db(
            state_name, id_en_context := await get_context_id_db("en")
        )
        if en_text is None:
            state_name = "None"
            text = await get_help_db(state_name, telegram_language)
            if text is None:
                en_text = await get_help_db(state_name, id_en_context)
                text: str = get_translate(  # type: ignore
                    TranslateRequest(
                        native_lang=telegram_language, foreign_lang="en", line=en_text
                    )
                ).translated_text
                await add_help_db(state=state_name, help_text=text, language=telegram_language)  # type: ignore
        else:
            text: str = get_translate(  # type: ignore
                TranslateRequest(
                    native_lang=telegram_language, foreign_lang="en", line=en_text
                )
            ).translated_text
            await add_help_db(state=state_name, help_text=text, language=telegram_language)  # type: ignore

    environment: Environment = jinja2.Environment()
    template: Template = environment.from_string(text)
    commands: dict = {f"_{str(i[2])}": f"/{i[0]}" for i in bot_commands}
    await msg.answer(template.render(**commands))
    # await msg.answer(text.format(**commands))


def register_handler_help(dp: Dispatcher) -> None:
    dp.message.register(cmd_help, Command(commands=["help"]))
