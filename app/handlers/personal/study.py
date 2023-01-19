import random
from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID
from zoneinfo import ZoneInfo

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.handlers.personal.callback_data_states import StudyFourOptionsCallbackData
from app.handlers.personal.keyboards import check_one_correct_from_four_study_keyboard

from app.base_functions.learning_sets import get_actual_card, get_three_random_words
from app.db_functions.personal import (
    get_user_id_db,
    get_all_items_according_context,
    get_user_context_db,
)
from app.exceptions.custom_exceptions import NotFullSetException
from app.tables import UserContext


class FSMStudyOneFromFour(StatesGroup):
    studying = State()


async def study_greeting(msg: types.Message, state: FSMContext) -> types.Message:
    """
    handler to show and activate <study> mode inside the menu

    as a result we have one word to study and to this word we
    have a keyboard of four words to choose one  correct
    """

    # from_user is None if messages sent to channels
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    user_id: Optional[UUID] = await get_user_id_db(msg.from_user.id)
    user_context: Optional[UserContext] = await get_user_context_db(msg.from_user.id)
    if user_id is None or user_context is None:
        return await msg.answer("To start studying follow /start command's way first")

    await msg.answer(text=f"Welcome to study, {msg.from_user.full_name}!")

    await state.set_state(FSMStudyOneFromFour.studying)

    start_time = datetime.now(tz=ZoneInfo("UTC"))
    end_time = start_time + timedelta(seconds=100)

    # getting lists of dict with text which according to user`s contexts, like [{'text': 'car'}, ...]
    try:
        texts_context_1: list[dict] = await get_all_items_according_context(
            user_context.context_1.id
        )
        texts_context_2: list[dict] = await get_all_items_according_context(
            user_context.context_2.id
        )
    except NotFullSetException:
        await state.clear()
        return await msg.answer(
            text="Minimum amount of words for studying mode is 4, enter required amount."
        )

    # here data gets into <MACHINE STATE> of the Telegram bot
    await state.set_data(
        {
            "end_time": end_time,
            "user_id": user_id,
            "texts_context_1": texts_context_1,
            "texts_context_2": texts_context_2,
            "context_1": user_context.context_1.id,
            "context_2": user_context.context_2.id,
        }
    )

    return await study_one_from_four(msg, state)


async def study_one_from_four(msg: types.Message, state: FSMContext) -> types.Message:
    state_data: dict = await state.get_data()

    if state_data["end_time"] > datetime.now(tz=ZoneInfo("UTC")):
        card: dict = await get_actual_card(state_data["user_id"])
        if not card:
            await state.clear()
            return await msg.answer(text="Run out of words to study")

        text_for_show: str = card["item_1"]
        right_answer: str = (
            card["item_2"] if text_for_show == card["item_1"] else card["item_1"]
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
        texts_answer_for_show: list[dict] = random.sample(
            [
                {"text": el["text"], "state": 0}
                for el in all_texts_answer
                if el["text"] != right_answer
            ],
            k=3,
        )
        # adding right answer
        texts_answer_for_show.append({"text": right_answer, "state": 1})

        return await msg.answer(
            text=card["item_1"],
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
    """
    In order to get <1> or <0> after user pics option
    use -> callback_query.data with returning types as 1 or
    0 in type<int> not bool
    """
    if callback_query.message is None:
        return await callback_query.answer("Pay attention the message is too old.")

    await callback_query.answer(
        f"{bool(callback_data.state)}"
    )  # response will be processed here

    symbol = "👍" if callback_data.state else "👎"
    await callback_query.message.edit_text(f"{callback_query.message.text} {symbol}")

    return await study_one_from_four(callback_query.message, state)


def register_handler_study(dp: Dispatcher) -> None:
    dp.message.register(
        study_greeting, Command(commands=["study", "изучение", "вивчення"])
    )

    # register handler two times for getting <1> or <0> reply from buttons
    dp.callback_query.register(
        handle_reply_after_four_words_studying,
        StudyFourOptionsCallbackData.filter(),
        FSMStudyOneFromFour.studying,
    )
