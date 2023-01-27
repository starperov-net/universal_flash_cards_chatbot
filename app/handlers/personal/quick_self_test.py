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
from app.handlers.personal.keyboards import what_to_do_with_card
from app.tables import UserContext

from aiogram.utils.text_decorations import HtmlDecoration


class FSMStudyOneFromFour(StatesGroup):
    """Creates <State Machine> for <study> handler.

    Inherits from <StateGroup> class
    """

    studying = State()


async def collect_data_for_fsm(user_context: UserContext) -> dict[str, Any]:
    """Collects data for storing in a <state machine> FSM.

    According UserContext the func collects
        end_time -> time when the study ends
        user_id -> a user identifier
        texts_context_1 -> a word to study in particular context
        texts_context_2 -> a word to study in opposite to texts_context_1 context
        context_1, context_2 -> two user's contexts

    Parameters:
        user_context:
            The <UserContext> class instance using the all_related() method
            https://piccolo-orm.readthedocs.io/en/latest/piccolo/query_types/objects.html#prefetching-related-objects.

    Returns:
        dict:
            example:
                {
                'end_time': datetime.datetime(2023, 1, 23, 18, 31, 2, 458654, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
                'user_id': UUID('ea89c754-61de-4f97-91f0-06a770d939b0'),
                'texts_context_1': [{'text': 'Например'}, {'text': 'быстрый'}],
                'texts_context_2': [{'text': 'break'}, {'text': 'but'}],
                'context_1': UUID('7eea0089-1dbb-4222-9184-37c22519c7bb'),
                'context_2': UUID('7a575cb2-b970-4396-a67b-3b6d8b809584')
                }
    """

    texts_context_1: list[dict] = await get_all_items_according_context(
        user_context.context_1.id
    )
    texts_context_2: list[dict] = await get_all_items_according_context(
        user_context.context_2.id
    )

    start_time = datetime.now(tz=ZoneInfo("UTC"))
    end_time = start_time + timedelta(seconds=100)

    return {
        "end_time": end_time,
        "user_id": user_context.user.id,
        "texts_context_1": texts_context_1,
        "texts_context_2": texts_context_2,
        "context_1": user_context.context_1.id,
        "context_2": user_context.context_2.id,
    }


async def study_greeting(msg: types.Message, state: FSMContext) -> types.Message:
    """A handler to start <study> mode.

    Activates studying mode with </study> command.
    As a result on a GUI we have one word to study
    and to this word we have a keyboard of four
    words to choose which one is correct.

    Parameters:
        msg:
            see base class
            Source: https://core.telegram.org/bots/api#message
        state:
            State Machine
            see base class

    Returns:
        msg:
            see base class
            Source: https://core.telegram.org/bots/api#message

    Raises:
        NotFullSetException:
             Minimum amount of words for studying mode is 4, enter required amount.
    """

    # from_user is None if messages sent to channels
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    user_context: Optional[UserContext] = await get_user_context_db(msg.from_user.id)
    if user_context is None or user_context.user.id is None:
        return await msg.answer("To start studying follow /start command's way first")

    await msg.answer(text=f"Welcome to study, {msg.from_user.full_name}!")

    try:
        data_for_fsm: dict[str, Any] = await collect_data_for_fsm(user_context)
    except NotFullSetException:
        return await msg.answer(
            text="Minimum amount of words for studying mode is 4, enter required amount."
        )

    await state.set_state(FSMStudyOneFromFour.studying)

    # here data gets into <MACHINE STATE> of the Telegram bot
    await state.set_data(data_for_fsm)

    return await quick_self_test(msg, state)


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

    word = [card["item_1"], card["item_2"]]
    random.shuffle(word)
    text_for_show: str
    answer: str
    text_for_show, answer = word
    hidden_answer = HtmlDecoration().spoiler(answer)
    answer = text_for_show + "\n" + hidden_answer
    return await msg.answer(
        text=answer, parse_mode="HTML", reply_markup=what_to_do_with_card(card_id=card['id']),
    )


def register_handler_quick_selt_test(dp: Dispatcher) -> None:
    dp.message.register(
        study_greeting, Command(commands=["selftest", "quick self-test", "швидка самоперевірка"])
    )

    # register handler two times for getting <1> or <0> reply from buttons
    # dp.callback_query.register(...
    #                            )
