from typing import List
from uuid import UUID

from aiogram.filters import Command

from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext

from app.base_functions.list_of_words import get_list_of_words
from app.db_functions.personal import get_card_by_idcard_db, delete_card_by_idcard_db, get_item_relation_by_id_db, \
    delete_item_relation_by_id_db, get_item_by_id_db, delete_item_by_id_db
from app.handlers.personal.callback_data_states import MyWordsCallbackData
from app.states.states import FSMMyWords


async def show_my_words(msg: types.Message, state: FSMContext) -> types.Message:
    """A handler to start <myWords> mode.

    Getting list of user words mode with </myWords> command.

    Parameters:
        msg: types.Message

        state:
            State Machine

    Returns:
        list_of_words:
            list[dict]

    """
    if msg.from_user is None:
        return await msg.answer("Messages sent to channels")

    list_of_words: List[dict] = await get_list_of_words(msg.from_user.id)
    # this loop is temporary
    for card in list_of_words:
        await msg.answer(
            text=f"{card['foreign_word']}    {card['native_word']}    {card['learning_status']}"
        )
    # this return is temporary
    return await msg.answer(text="It's all")


async def delete_customs_card(callback_query: types.CallbackQuery,
                              callback_data: MyWordsCallbackData,
                              state: FSMContext,
                              ) -> types.Message:
    """
    запам'ятати id item_relation
    видалити card  по  id_card

    перевірити author у  item_relation
    если author = user
        запам'ятати id  item1 item2
        видалити item_relation

    перевірити author у  item1
    если author = user
        видалити item1

    перевірити author у  item2
    если author = user
        видалити item2
    """

    card_id: UUID = state.get_data('card_id') #  card_id  передається через state  чи через callback_data
    card_dict: dict = await get_card_by_idcard_db(card_id)

    item_relation_id: UUID = card_dict['item_relation']
    await delete_card_by_idcard_db(card_id)
    item_relation_dict: dict = await get_item_relation_by_id_db(item_relation_id)

    # check item_relation for author
    if item_relation_dict['author'] == card_dict['author']:
        await delete_item_relation_by_id_db(item_relation_id)

        # check items for author. Delete or not delete those items
        for item in (item_relation_dict['item_1'], item_relation_dict['item_2']):
            item_dict: dict = await get_item_by_id_db(item)

            if item_dict['author'] == card_dict['author']:
                await delete_item_by_id_db(item)

    return await callback_query.answer("😢 deleted 😢")


def register_handler_mywords(dp: Dispatcher) -> None:
    """A handler's registrator.

    Parameters:
        dp:
            see base class

    Returns:
        None
    """

    dp.message.register(
        show_my_words,
        Command(commands=["mywords", "список моїх слів", "список моих слов"]),
    )
    dp.callback_query.register(delete_customs_card, FSMMyWords.mywords)
