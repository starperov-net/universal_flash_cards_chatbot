from typing import Optional

from uuid import UUID

from aiogram import Dispatcher, types
from aiogram.filters import Command

from app.base_functions.learning_sets import get_actual_card
from app.db_functions.personal import get_user_id_db
from app.exceptions.custom_exceptions import NotFullSetException
from app.handlers.personal.callback_data_states import StudyFourOptionsCallbackData
from app.handlers.personal.keyboards import check_one_correct_from_four_study_keyboard
from app.tables import Item


async def study(msg: types.Message) -> types.Message:
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

    async for card in get_actual_card(user_id, authors=None):
        query = f"""
        SELECT i.text
        FROM item i
        WHERE(i.context='{str(card['context_item_2'])}')
        ORDER BY random()
        ASC
        LIMIT 3;
        """
        res = await Item.raw(query)

        words_to_show = [{'text': el['text'], 'state': 0} for el in res]

        words_to_show.append({'text': card['item_2'], 'state': 1})

        try:
            if len(words_to_show) < 4:
                raise NotFullSetException
        except NotFullSetException:
            return await msg.answer(text=f"Minimum amount of words for studying mode is 4, enter required amount.")
        return await msg.answer(
            text=card['item_1'],
            reply_markup=check_one_correct_from_four_study_keyboard(
                words_list=words_to_show,
                card_id=card['id'],
                memorization_stage=card['memorization_stage'],
                repetition_level=card['repetition_level']
            )
        )


async def handle_reply_after_four_words_studying(
        callback_query: types.CallbackQuery, callback_data: StudyFourOptionsCallbackData
) -> None:
    """
    In order to get <True> or <False> after user pics option
    use -> callback_query.data with returning types as True or
    False in type<str> not bool
    """
    await callback_query.answer(f'callback_data: {callback_data}')


def register_handler_study(dp: Dispatcher) -> None:
    dp.message.register(study, Command(commands=["study", "изучение", "вивчення"]))

    # register handler two times for getting <True> or <False> reply from buttons
    dp.callback_query.register(
        handle_reply_after_four_words_studying, StudyFourOptionsCallbackData.filter()
    )
