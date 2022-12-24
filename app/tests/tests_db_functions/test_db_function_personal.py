import typing as t
from unittest import IsolatedAsyncioTestCase

import aiogram
import pytest
from parameterized import parameterized
from piccolo.conf.apps import Finder
from piccolo.table import Table, create_db_tables_sync, drop_db_tables_sync


from app.db_functions.personal import add_user_db, add_item_db, get_translated_word_db
from app.tables import User, ItemRelation, Item, UserContext, Context
from app.tests.utils import (TELEGRAM_USER_1, TELEGRAM_USER_2,
                             TABLE_USER_1, TABLE_USER_2, TABLE_USER_3, TABLE_USER_GOOGLE,
                             TABLE_USER_CONTEXT_1_uk_en, TABLE_USER_CONTEXT_2_uk_en, TABLE_USER_CONTEXT_3_ru_de,
                             TABLE_ITEM_en_auto, TABLE_ITEM_de_auto, TABLE_ITEM_de_wagen,
                             TABLE_ITEM_uk_automobil, TABLE_ITEM_ru_mashina,
                             TABLE_CONTEXT_en, TABLE_CONTEXT_de, TABLE_CONTEXT_uk, TABLE_CONTEXT_ru,

                             TABLE_ITEM_RELATION_1_ru_de, TABLE_ITEM_RELATION_1_uk_en,
                             TABLE_ITEM_RELATION_GOOGLE_en_uk, TABLE_ITEM_RELATION_GOOGLE_ru_de,
                             TABLE_ITEM_RELATION_3_ru_de)


TABLES: t.List[t.Type[Table]] = Finder().get_table_classes()


class TestVerificationOfRecordedDataToDB(IsolatedAsyncioTestCase):
    def setUp(self):
        create_db_tables_sync(*TABLES)

    def tearDown(self):
        drop_db_tables_sync(*TABLES)

    @parameterized.expand([(TELEGRAM_USER_1,), (TELEGRAM_USER_2,)])
    @pytest.mark.asyncio
    async def test_add_user_db(
        self, telegram_user: aiogram.types.User
    ) -> None:
        user: User = await add_user_db(telegram_user)
        assert user.telegram_user_id == telegram_user.id
        assert user.first_name == telegram_user.first_name
        assert user.last_name == (telegram_user.last_name or "")
        assert user.user_name == (telegram_user.username or "")
        assert user.telegram_language == (telegram_user.language_code or "")
        
    @pytest.mark.asyncio
    async def test_add_item_db(self) -> None:
        text: str = 'window'
        context: Context = Context(name='English', name_alfa2='en')
        await context.save()
        await TABLE_USER_1.save()
        item: Item = await add_item_db(
            author=TABLE_USER_1.id,
            context=context.id,
            text=text
        )

        assert item.author == TABLE_USER_1.id
        assert item.context == context.id
        assert item.text == 'window'


class TestGetItemRelation(IsolatedAsyncioTestCase):
    def setUp(self):
        drop_db_tables_sync(*TABLES)
        create_db_tables_sync(*TABLES)
        Context.insert(
            TABLE_CONTEXT_en,
            TABLE_CONTEXT_de,
            TABLE_CONTEXT_uk,
            TABLE_CONTEXT_ru
        ).run_sync()
        User.insert(
            TABLE_USER_GOOGLE,
            TABLE_USER_1,
            TABLE_USER_2,
            TABLE_USER_3
        ).run_sync()
        UserContext.insert(
            TABLE_USER_CONTEXT_1_uk_en,
            TABLE_USER_CONTEXT_2_uk_en,
            TABLE_USER_CONTEXT_3_ru_de
        ).run_sync()
        Item.insert(
            TABLE_ITEM_en_auto,
            TABLE_ITEM_de_auto,
            TABLE_ITEM_de_wagen,
            TABLE_ITEM_uk_automobil,
            TABLE_ITEM_ru_mashina
        ).run_sync()
        ItemRelation.insert(
            TABLE_ITEM_RELATION_1_uk_en,
            TABLE_ITEM_RELATION_1_ru_de,
            TABLE_ITEM_RELATION_GOOGLE_en_uk,
            TABLE_ITEM_RELATION_3_ru_de,
            TABLE_ITEM_RELATION_GOOGLE_ru_de
        ).run_sync()

    def tearDown(self):
        drop_db_tables_sync(*TABLES)

    @parameterized.expand([('wagen', 'машина', 3), ('машина', None, 1),
                           ('автомобіль', 'auto', 1),
                           ('auto', 'автомобіль', 1),
                           ('auto', 'автомобіль', 2),
                           ('машина', 'auto', 3),

                           ])
    @pytest.mark.asyncio
    async def test_get_translated_word_db(
            self, word: str, translated_word: str, telegram_user_id: int
    ) -> None:
        answer: t.Optional[str] = await get_translated_word_db(word, telegram_user_id)
        assert answer == translated_word
