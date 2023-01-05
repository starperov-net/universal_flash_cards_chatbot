from typing import Optional
# from uuid import UUID
import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
#
# import app.handlers.personal.keyboards as kb
# from app.base_functions.translator import get_translate
from app.db_functions.personal import get_list_cards_to_study_db
# from app.handlers.personal.callback_data_states import ToStudyCallbackData
#
# from app.scheme.transdata import TranslateRequest, TranslateResponse
from app.tables import Card, User, UserContext, Item, ItemRelation
# from app.tests.utils import TELEGRAM_USER_GOOGLE


async def study(msg: types.Message) -> types.Message:
    # from_user is None if messages sent to channels
    logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ENTERED')

    if msg.from_user is None:

        logging.info('******************************************* NONE')

        return await msg.answer("Messages sent to channels")

    logging.info(f'==========================================')
    logging.info(msg.from_user)
    logging.info(f'==========================================')

    await msg.answer(text=f"Welcome to study, {msg.from_user.full_name}!")
    list_cards_for_studying: list[Card] = await get_list_cards_to_study_db(msg.from_user.id)
    for card in list_cards_for_studying:
        logging.info('******************************************* CARD START')
        logging.info(card.__dict__)
        logging.info('------------------------------------------------------')
        logging.info(card.user.__dict__)
        # logging.info(card.author)
        logging.info('******************************************* CARD FINISH')
    logging.info(f'-----------------{list_cards_for_studying}')


# async def study_greeting(msg: types.Message) -> None:
#     await msg.answer(text=f"{msg.from_user.full_name}, welcome to study!")


def register_handler_study(dp: Dispatcher) -> None:
    dp.message.register(study, Command(commands=["study", "изучение", "вивчення"]))
