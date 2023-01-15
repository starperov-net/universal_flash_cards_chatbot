from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.base_functions.learning_sets import get_actual_card
from app.db_functions.personal import get_user_id_db, get_three_random_words
from app.exceptions.custom_exceptions import NotFullSetException
from app.handlers.personal.callback_data_states import StudyFourOptionsCallbackData
from app.handlers.personal.keyboards import check_one_correct_from_four_study_keyboard
from app.tables import Item


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
    if user_id is None:
        return await msg.answer("To start studying follow /start command's way first")

    await msg.answer(text=f"Welcome to study, {msg.from_user.full_name}!")
    start_time = datetime.now(tz=ZoneInfo("UTC"))
    end_time = start_time + timedelta(seconds=300)
    await state.set_data({"end_time": end_time, "user_id": user_id})
    await state.set_state(FSMStudyOneFromFour.studying)
    await study_one_from_four(msg, state)


async def study_one_from_four(msg: types.Message, state: FSMContext) -> types.Message:
    state_data: dict = await state.get_data()

    if state_data["end_time"] > datetime.now(tz=ZoneInfo("UTC")):
        card: dict = await get_actual_card(state_data["user_id"])
        if not card:
            await state.clear()
            return await msg.answer(text=f"Run out of words to study")
        try:
            three_random_words: list[dict] = await get_three_random_words(
                card["context_item_2"]
            )
        except NotFullSetException:
            await state.clear()
            return await msg.answer(
                text=f"Minimum amount of words for studying mode is 4, enter required amount."
            )

        # generating a list of 4 dict like {"text": "some_word", "state": 0}
        words_to_show: list[dict] = [
            {"text": el["text"], "state": 0} for el in three_random_words
        ]
        words_to_show.append({"text": card["item_2"], "state": 1})

        return await msg.answer(
            text=card["item_1"],
            reply_markup=check_one_correct_from_four_study_keyboard(
                words_list=words_to_show,
                card_id=card["id"],
                memorization_stage=card["memorization_stage"],
                repetition_level=card["repetition_level"],
            ),
        )
    else:
        await state.clear()
        await msg.answer(text=f"Training time expired.")


async def handle_reply_after_four_words_studying(
    callback_query: types.CallbackQuery,
    callback_data: StudyFourOptionsCallbackData,
    state: FSMContext,
) -> None:
    """
    In order to get <True> or <False> after user pics option
    use -> callback_query.data with returning types as True or
    False in type<str> not bool
    """

    await callback_query.answer(
        f"{bool(callback_data.state)}"
    )  # response will be processed here

    await study_one_from_four(callback_query.message, state)


def register_handler_study(dp: Dispatcher) -> None:
    dp.message.register(
        study_greeting, Command(commands=["study", "изучение", "вивчення"])
    )
    # dp.message.register(study_one_from_four, FSMStudyOneFromFour.studying)

    # register handler two times for getting <True> or <False> reply from buttons
    dp.callback_query.register(
        handle_reply_after_four_words_studying, StudyFourOptionsCallbackData.filter()
    )
