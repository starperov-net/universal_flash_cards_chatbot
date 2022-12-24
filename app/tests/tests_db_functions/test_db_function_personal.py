import typing as t
from unittest import IsolatedAsyncioTestCase

import aiogram
import pytest
from parameterized import parameterized
from piccolo.conf.apps import Finder
from piccolo.table import Table, create_db_tables_sync, drop_db_tables_sync

from app.db_functions.personal import add_user_db, add_item_db, add_item_relation_db
from app.tables import User, ItemRelation, Item
from app.tests.utils import TELEGRAM_USER_1, TELEGRAM_USER_2, TABLE_USER_1, CONTEXT_EN

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
        await CONTEXT_EN.save()
        await TABLE_USER_1.save()
        item: Item = await add_item_db(
            author=TABLE_USER_1.id,
            context=CONTEXT_EN.id,
            text=text
        )

        assert item.author == TABLE_USER_1.id
        assert item.context == CONTEXT_EN.id
        assert item.text == 'window'


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
