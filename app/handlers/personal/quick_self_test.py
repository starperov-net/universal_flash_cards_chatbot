from datetime import datetime, timedelta
import random
from typing import Any, Optional
from zoneinfo import ZoneInfo

from aiogram import types

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.base_functions.learning_sets import get_actual_card
from app.db_functions.personal import get_user_context_db, get_all_items_according_context
from app.exceptions.custom_exceptions import NotFullSetException
from app.tables import UserContext

from aiogram.utils.text_decorations import  HtmlDecoration
from .study import FSMStudyOneFromFour, collect_data_for_fsm, study_greeting


async def quick_self_test(msg: types.Message, state: FSMContext) -> types.Message:
    state_data: dict[str, Any] = await state.get_data()
    # <tg-spoiler>answer</tg-spoiler>

    if state_data["end_time"] < datetime.now(tz=ZoneInfo("UTC")):
        await state.clear()
        return await msg.answer(text="Training time has expired.")

    card: dict[str, Any] = await get_actual_card(state_data["user_id"])
    if not card:
        await state.clear()
        return await msg.answer(text="Run out of words to study")

    text_for_show: str
    answer: str
    text_for_show, answer = random.shuffle([card["item_1"], card["item_2"]])
    hidden_answer = HtmlDecoration().spoiler(answer)
    answer = text_for_show + "\n" + hidden_answer
    return await msg.answer(
        text=answer, parse_mode="HTML",
    )


def register_handler_quick_selt_test(dp: Dispatcher) -> None:
    dp.message.register(
        quick_self_test, Command(commands=["selftest", "quick self-test", "швидка самоперевірка"])
    )

    # register handler two times for getting <1> or <0> reply from buttons
    # dp.callback_query.register(...
    #                            )
