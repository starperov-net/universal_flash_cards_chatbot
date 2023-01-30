import random
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from uuid import UUID
from zoneinfo import ZoneInfo

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.base_functions.learning_sets import (get_actual_card,
                                              set_res_studying_card)
from app.db_functions.personal import (get_all_items_according_context,
                                       get_user_context_db)
from app.exceptions.custom_exceptions import (NotFullSetException,
                                              NotNoneValueError)
from app.handlers.personal.callback_data_states import \
    StudyFourOptionsCallbackData
from app.handlers.personal.keyboards import \
    check_one_correct_from_four_study_keyboard
from app.serializers import Card
from app.tables import UserContext


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

    return await study_one_from_four(msg, state)


async def study_one_from_four(msg: types.Message, state: FSMContext) -> types.Message:
    """Creates and displays user's keyboard.

    Creates and displays one word to study and
    to this word a keyboard of four words for choosing
    which one is correct OR a message that studying
    has expired.

    Parameters:
        msg:
            see base class
            Source: https://core.telegram.org/bots/api#message
        state:
            State Machine where save data:
            {
                'end_time': datetime.datetime(2023, 1, 30, 9, 45, 22, 55017, tzinfo=zoneinfo.ZoneInfo(key='UTC')), *
                'user_id': UUID('08ef015a-36d8-49e7-8b0b-8d86f951a78e'), *
                'texts_context_1': [{'text': 'дієта'}, {'text': 'сюрприз'}, ...], *
                'texts_context_2': [{'text': 'pen'}, {'text': 'flat'}, ...], *
                'context_1': UUID('86edaed5-336b-4b3b-b103-7dbb36f1ad34'), *
                'context_2': UUID('7e831026-0c60-448e-9669-3c085d5f6903') *
            }
            * - The value is unchanged throughout the cycle


    Returns:
        msg:
            see base class
            Source: https://core.telegram.org/bots/api#message
    """

    state_data: dict[str, Any] = await state.get_data()

    if state_data["end_time"] > datetime.now(tz=ZoneInfo("UTC")):
        card: dict[str, Any] = await get_actual_card(state_data["user_id"])
        if not card:
            await state.clear()
            return await msg.answer(text="Run out of words to study")

        texts: list[str] = [card["item_1"], card["item_2"]]
        random.shuffle(texts)
        text_for_show, correct_answer = texts

        await state.update_data(
            {
                "correct_translation": {
                    "text_for_show": text_for_show,
                    "correct_answer": correct_answer,
                }
            }
        )

        context_answer: UUID = (
            card["context_item_2"]
            if text_for_show == card["item_1"]
            else card["context_item_1"]
        )
        all_texts_answer: list[dict] = (
            state_data["texts_context_2"]
            if context_answer == state_data["context_2"]
            else state_data["texts_context_1"]
        )

        # generating a list of 3 dict like {"text": "some_word", "state": 0}
        texts_answer_for_show: list[dict[str, Any]] = random.sample(
            [
                {"text": el["text"], "state": 0}
                for el in all_texts_answer
                if el["text"] != correct_answer
            ],
            k=3,
        )

        texts_answer_for_show.append({"text": correct_answer, "state": 1})

        return await msg.answer(
            text=text_for_show,
            reply_markup=check_one_correct_from_four_study_keyboard(
                words_list=texts_answer_for_show,
                card_id=card["id"],
                memorization_stage=card["memorization_stage"],
                repetition_level=card["repetition_level"],
            ),
        )
    else:
        await state.clear()
        return await msg.answer(text="Training time has expired.")


async def handle_reply_after_four_words_studying(
    callback_query: types.CallbackQuery,
    callback_data: StudyFourOptionsCallbackData,
    state: FSMContext,
) -> Union[types.Message, bool]:
    """Processes the result for study mode keyboard work.

    Up to dates DB data in Card table according to:
    - memorization_stage
    - repetition_level
    - result answer (True, False).
    If the user did not answer in the current session, the data
    in the DB is not updated.

    Parameters:
        callback_query:
            see base class
        callback_data:
            see base class
        state:
            State Machine where save data current session:
            {
                'end_time': datetime.datetime(2023, 1, 30, 9, 45, 22, 55017, tzinfo=zoneinfo.ZoneInfo(key='UTC')),
                'user_id': UUID('08ef015a-36d8-49e7-8b0b-8d86f951a78e'), *
                'texts_context_1': [{'text': 'дієта'}, {'text': 'сюрприз'}, ...] *
                'texts_context_2': [{'text': 'pen'}, {'text': 'flat'}, ...] *
                'context_1': UUID('86edaed5-336b-4b3b-b103-7dbb36f1ad34'), *
                'context_2': UUID('7e831026-0c60-448e-9669-3c085d5f6903'), *
                'correct_translation': {'text_for_show': 'виправити', 'correct_answer': 'fix'} **
            }
            * - The value is unchanged throughout the cycle
            ** - Value change on every cycle
    Return:
        Updates the previous answer, removes the keyboard from it
        and adds the correct word and symbol to the answer text -
        the answer was correct or not.
    """

    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    symbol = "🤓" if callback_data.state else "🤨"

    state_data: dict[str, Any] = await state.get_data()
    correct_translation: Optional[dict] = state_data.get("correct_translation")

    # when the user replied not in the current session
    if (
        correct_translation is None
        or correct_translation["text_for_show"] != callback_query.message.text
    ):
        await callback_query.answer("Message is outdated.")
        return await callback_query.message.edit_text(
            f"{callback_query.message.text}            {symbol} "
        )
    correct_answer: str = correct_translation["correct_answer"]

    try:
        await set_res_studying_card(
            Card(
                id=callback_data.card_id,
                memorization_stage=callback_data.memorization_stage,
                repetition_level=callback_data.repetition_level,
            ),
            result=bool(callback_data.state),
        )
    except NotNoneValueError:
        await state.clear()
        return await callback_query.answer("😢 Something went wrong 😢")

    await callback_query.message.edit_text(
        f"{callback_query.message.text}    ({correct_answer})        {symbol} "
    )

    del state_data["correct_translation"]
    await state.set_data(state_data)

    return await study_one_from_four(callback_query.message, state)


def register_handler_study(dp: Dispatcher) -> None:
    """A handler's registrator.

    Parameters:
        dp:
            see base class

    Returns:
        None
    """

    dp.message.register(
        study_greeting, Command(commands=["study", "изучение", "вивчення"])
    )

    # register handler two times for getting <1> or <0> reply from buttons
    dp.callback_query.register(
        handle_reply_after_four_words_studying,
        StudyFourOptionsCallbackData.filter(),
        FSMStudyOneFromFour.studying,
    )
