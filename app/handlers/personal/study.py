from typing import Optional

# from uuid import UUID
import logging
from uuid import UUID

import piccolo
from aiogram import Dispatcher, types
from aiogram.filters import Command

from app.base_functions.learning_sets import get_actual_card

# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
#
# import app.handlers.personal.keyboards as kb
# from app.base_functions.translator import get_translate
from app.db_functions.personal import get_list_cards_to_study_db, get_user_id_db
from app.handlers.personal.keyboards import check_one_correct_from_four_study_keyboard

# from app.handlers.personal.callback_data_states import ToStudyCallbackData
#
# from app.scheme.transdata import TranslateRequest, TranslateResponse
from app.tables import Card, User, UserContext, Item, ItemRelation

# from app.tests.utils import TELEGRAM_USER_GOOGLE


async def study(msg: types.Message) -> types.Message:
    # from_user is None if messages sent to channels
    logging.info(">" * 75, " ENTERED")

    if msg.from_user is None:

        logging.info("*" * 75, " NONE")

        return await msg.answer("Messages sent to channels")

    logging.info(f"==========================================")

    user_id: Optional[UUID] = await get_user_id_db(msg.from_user.id)
    if user_id is None:
        return await msg.answer("To start studying follow /start command's way first")

    await msg.answer(text=f"Welcome to study, {msg.from_user.full_name}!")

    """
    output: all data for last usercontext
        dict {
            'id': UUID (for actual Card),
            'memorization_stage': int (for actual Card),
            'repetition_level': int (for actual Card),
            'last_date': datetime (for actual Card),
            'item_1': str,
            'item_2': str
    }
    """
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
        words_to_show = [el["text"] for el in res]
        words_to_show.append(card["item_2"])
        # words_to_learn = Item.select(Item.text).where(Item.context == card['context_item_2']).order_by(OrderByRaw('random()')).limit(3).run_sync()
        # await msg.answer(text=f"DICT - {card}")
        await msg.answer(
            text=f"ITEM_1 - {card['item_1']}",
            reply_markup=check_one_correct_from_four_study_keyboard(words_to_show),
        )
        # await msg.answer(text=f"ITEM_2 - {card['item_2']}")

    # list_cards_for_studying: list[Card] = await get_list_cards_to_study_db(msg.from_user.id)
    # for card in list_cards_for_studying:
    #     logging.info('******************************************* CARD START')
    #     logging.info(card.__dict__)
    #     logging.info('------------------------------------------------------')
    #     logging.info(card.user.__dict__)
    #     # logging.info(card.author)
    #     logging.info('******************************************* CARD FINISH')
    # logging.info(f'-----------------{list_cards_for_studying}')


# async def study_greeting(msg: types.Message) -> None:
#     await msg.answer(text=f"{msg.from_user.full_name}, welcome to study!")


def register_handler_study(dp: Dispatcher) -> None:
    dp.message.register(study, Command(commands=["study", "изучение", "вивчення"]))
