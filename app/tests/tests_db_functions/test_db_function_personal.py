import typing as t
from unittest import IsolatedAsyncioTestCase

import aiogram
import pytest
from parameterized import parameterized
from piccolo.conf.apps import Finder
from piccolo.table import Table, create_db_tables_sync, drop_db_tables_sync

from app.db_functions.personal import add_user_db, add_item_db, add_item_relation_db, get_translated_text_db
from app.tables import User, ItemRelation, Item, UserContext, Context
from app.tests.utils import (TELEGRAM_USER_1, TELEGRAM_USER_2)
from app.tests.tests_db_functions.utils import (USER_1, USER_2, USER_3, USER_GOOGLE,
                                                USER_CONTEXT_1_uk_en, USER_CONTEXT_2_uk_en, USER_CONTEXT_3_ru_de,
                                                ITEM_en_auto, ITEM_de_auto, ITEM_de_wagen,
                                                ITEM_uk_automobil, ITEM_ru_mashina,
                                                CONTEXT_en, CONTEXT_de, CONTEXT_uk, CONTEXT_ru,
                                                ITEM_RELATION_1_ru_de, ITEM_RELATION_1_uk_en,
                                                ITEM_RELATION_GOOGLE_en_uk, ITEM_RELATION_GOOGLE_ru_de,
                                                ITEM_RELATION_3_ru_de)


TABLES: t.List[t.Type[Table]] = Finder().get_table_classes()


class TestVerificationOfRecordedDataToDB(IsolatedAsyncioTestCase):
    def setUp(self):
        create_db_tables_sync(*TABLES, if_not_exists=True)

    def tearDown(self):
        drop_db_tables_sync(*TABLES)

    @parameterized.expand([(TELEGRAM_USER_1,), (TELEGRAM_USER_2,)])
    async def test_add_user_db(
        self, telegram_user: aiogram.types.User
    ) -> None:
        user: User = await add_user_db(telegram_user)
        assert user.telegram_user_id == telegram_user.id
        assert user.first_name == telegram_user.first_name
        assert user.last_name == (telegram_user.last_name or "")
        assert user.user_name == (telegram_user.username or "")
        assert user.telegram_language == (telegram_user.language_code or "")

    async def test_add_item_db(self) -> None:
        text: str = 'window'
        await CONTEXT_en.save()
        await USER_1.save()
        item: Item = await add_item_db(
            author=USER_1.id,
            context=CONTEXT_en.id,
            text=text
        )

        assert item.author == USER_1.id
        assert item.context == CONTEXT_en.id
        assert item.text == 'window'


class TestGetItemRelation(IsolatedAsyncioTestCase):
    def setUp(self):
        drop_db_tables_sync(*TABLES)
        create_db_tables_sync(*TABLES)
        Context.insert(
            CONTEXT_en,
            CONTEXT_de,
            CONTEXT_uk,
            CONTEXT_ru
        ).run_sync()
        User.insert(
            USER_GOOGLE,
            USER_1,
            USER_2,
            USER_3
        ).run_sync()
        UserContext.insert(
            USER_CONTEXT_1_uk_en,
            USER_CONTEXT_2_uk_en,
            USER_CONTEXT_3_ru_de
        ).run_sync()
        Item.insert(
            ITEM_en_auto,
            ITEM_de_auto,
            ITEM_de_wagen,
            ITEM_uk_automobil,
            ITEM_ru_mashina
        ).run_sync()
        ItemRelation.insert(
            ITEM_RELATION_1_uk_en,
            ITEM_RELATION_1_ru_de,
            ITEM_RELATION_GOOGLE_en_uk,
            ITEM_RELATION_3_ru_de,
            ITEM_RELATION_GOOGLE_ru_de
        ).run_sync()

    def tearDown(self):
        drop_db_tables_sync(*TABLES)

    @parameterized.expand([('wagen', 'машина', 3, USER_CONTEXT_3_ru_de.context_1, USER_CONTEXT_3_ru_de.context_2),
                           ('машина', None, 1, USER_CONTEXT_1_uk_en.context_1, USER_CONTEXT_1_uk_en.context_2),
                           ('автомобіль', 'auto', 1, USER_CONTEXT_1_uk_en.context_1, USER_CONTEXT_1_uk_en.context_2),
                           ('auto', 'автомобіль', 1, USER_CONTEXT_1_uk_en.context_1, USER_CONTEXT_1_uk_en.context_2),
                           ('auto', 'автомобіль', 2, USER_CONTEXT_2_uk_en.context_1, USER_CONTEXT_2_uk_en.context_2),
                           ('машина', 'auto', 3, USER_CONTEXT_3_ru_de.context_1, USER_CONTEXT_3_ru_de.context_2),

                           ])
    @pytest.mark.asyncio
    async def test_get_translated_text_db(
            self, word: str, translated_word: str, telegram_user_id: int, context_1: Context.id, context_2: Context.id
    ) -> None:
        answer: t.Optional[str] = await get_translated_text_db(word, telegram_user_id, context_1, context_2)
        assert answer == translated_word


@pytest.mark.asyncio
async def test_add_item_relation_db(user, item_uk, item_en) -> None:
    item_relation: ItemRelation = await add_item_relation_db(
        author=user.id,
        item_1=item_en.id,
        item_2=item_uk.id
    )
    assert item_relation.author == user.id
    assert item_relation.item_1 == item_en.id
    assert item_relation.item_2 == item_uk.id
