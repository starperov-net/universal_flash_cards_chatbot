from aiogram.filters.callback_data import CallbackData
from asyncpg.pgproto.pgproto import UUID


class ToStudyCallbackData(CallbackData, prefix='my_callback'):
    text: str
    item_relation_id: UUID
