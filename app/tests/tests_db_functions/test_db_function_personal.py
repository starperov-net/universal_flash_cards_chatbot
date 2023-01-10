import typing as t
from unittest import IsolatedAsyncioTestCase
from uuid import UUID

import aiogram
import pytest
from parameterized import parameterized  # type: ignore
from piccolo.conf.apps import Finder
from piccolo.table import Table, create_db_tables_sync, drop_db_tables_sync

from app.db_functions.personal import (
    add_item_relation_db,
    get_or_create_user_db,
    get_or_create_item_db,
    get_item_relation_by_text_db,
    get_translated_text_from_item_relation,
)

from app.tables import User, ItemRelation, Item, UserContext, Context
from app.tests.utils import TELEGRAM_USER_1, TELEGRAM_USER_2
from app.tests.tests_db_functions.utils import (
    USER_1,
    USER_2,
    USER_3,
    USER_GOOGLE,
    USER_CONTEXT_1_uk_en,
    USER_CONTEXT_2_uk_en,
    USER_CONTEXT_3_ru_de,
    ITEM_en_auto,
    ITEM_de_auto,
    ITEM_de_wagen,
    ITEM_uk_automobil,
    ITEM_ru_mashina,
    CONTEXT_en,
    CONTEXT_de,
    CONTEXT_uk,
    CONTEXT_ru,
    ITEM_RELATION_1_ru_de,
    ITEM_RELATION_1_uk_en,
    ITEM_RELATION_GOOGLE_en_uk,
    ITEM_RELATION_GOOGLE_ru_de,
    ITEM_RELATION_3_ru_de,
)


TABLES: t.List[t.Type[Table]] = Finder().get_table_classes()


class TestVerificationOfRecordedDataToDB(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        create_db_tables_sync(*TABLES, if_not_exists=True)

    def tearDown(self) -> None:
        drop_db_tables_sync(*TABLES)

    @parameterized.expand([(TELEGRAM_USER_1,), (TELEGRAM_USER_2,)])
    async def test_get_or_create_user_db(
        self, telegram_user: aiogram.types.User
    ) -> None:
        user: User = await get_or_create_user_db(telegram_user)
        assert user.telegram_user_id == telegram_user.id
        assert user.first_name == telegram_user.first_name
        assert user.last_name == (telegram_user.last_name or "")
        assert user.user_name == (telegram_user.username or "")
        assert user.telegram_language == (telegram_user.language_code or "")

    async def test_get_or_create_item_db(self) -> None:
        text: str = "window"
        await CONTEXT_en.save()
        await USER_1.save()
        await get_or_create_item_db(
            author_id=USER_1.id, context_id=CONTEXT_en.id, text=text
        )
        item: Item = await Item.objects().get(Item.text == text)
        assert item.author == USER_1.id
        assert item.context == CONTEXT_en.id


class TestGetTranslatedText(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        drop_db_tables_sync(*TABLES)
        create_db_tables_sync(*TABLES)
        Context.insert(CONTEXT_en, CONTEXT_de, CONTEXT_uk, CONTEXT_ru).run_sync()
        User.insert(USER_GOOGLE, USER_1, USER_2, USER_3).run_sync()
        UserContext.insert(
            USER_CONTEXT_1_uk_en, USER_CONTEXT_2_uk_en, USER_CONTEXT_3_ru_de
        ).run_sync()
        Item.insert(
            ITEM_en_auto,
            ITEM_de_auto,
            ITEM_de_wagen,
            ITEM_uk_automobil,
            ITEM_ru_mashina,
        ).run_sync()
        ItemRelation.insert(
            ITEM_RELATION_1_uk_en,
            ITEM_RELATION_1_ru_de,
            ITEM_RELATION_GOOGLE_en_uk,
            ITEM_RELATION_3_ru_de,
            ITEM_RELATION_GOOGLE_ru_de,
        ).run_sync()

    def tearDown(self) -> None:
        drop_db_tables_sync(*TABLES)

    @parameterized.expand(
        [
            ("wagen", "машина", USER_CONTEXT_3_ru_de),
            ("автомобіль", "auto", USER_CONTEXT_1_uk_en),
            ("auto", "автомобіль", USER_CONTEXT_1_uk_en),
            ("auto", "автомобіль", USER_CONTEXT_2_uk_en),
            ("машина", "auto", USER_CONTEXT_3_ru_de),
        ]
    )
    @pytest.mark.asyncio
    async def test_get_translated_text_from_db(
        self, word: str, translated_word: str, user_context: UserContext
    ) -> None:
        item_relation: t.Optional[ItemRelation] = await get_item_relation_by_text_db(
            word, user_context
        )
        answer: str = await get_translated_text_from_item_relation(word, item_relation)  # type: ignore
        assert answer == translated_word

    async def test_get_item_relation_by_text_return_None(self) -> None:
        word: str = "машина"
        user_context: UserContext = USER_CONTEXT_1_uk_en
        item_relation: t.Optional[ItemRelation] = await get_item_relation_by_text_db(
            word, user_context
        )
        assert item_relation is None


@pytest.mark.asyncio
async def test_add_item_relation_db(user: User, item_uk: Item, item_en: Item) -> None:
    item_relation_id: UUID = await add_item_relation_db(
        author_id=user.id, item_1_id=item_en.id, item_2_id=item_uk.id
    )
    item_relation: ItemRelation = await ItemRelation.objects().get(
        ItemRelation.id == item_relation_id
    )
    assert item_relation.author == user.id
    assert item_relation.item_1 == item_en.id
    assert item_relation.item_2 == item_uk.id
