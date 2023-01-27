from typing import Generator

import pytest_asyncio
from piccolo.table import create_db_tables_sync, drop_db_tables_sync

from app.tables import Context, Item, User
from app.tests.tests_db_functions.test_db_function_personal import TABLES
from app.tests.tests_db_functions.utils import (
    USER_1,
    CONTEXT_en,
    CONTEXT_uk,
    ITEM_en_auto,
    ITEM_uk_automobil,
)


@pytest_asyncio.fixture
async def user() -> User:
    await User.insert(USER_1)
    return USER_1


@pytest_asyncio.fixture
async def context_uk() -> Context:
    await Context.insert(CONTEXT_uk)
    return CONTEXT_uk


@pytest_asyncio.fixture
async def context_en() -> Context:
    await Context.insert(CONTEXT_en)
    return CONTEXT_en


@pytest_asyncio.fixture
async def item_uk(user: User, context_uk: Context) -> Item:
    await Item.insert(ITEM_uk_automobil)
    return ITEM_uk_automobil


@pytest_asyncio.fixture
async def item_en(user: User, context_en: Context) -> Item:
    await Item.insert(ITEM_en_auto)
    return ITEM_en_auto


def setup() -> None:
    create_db_tables_sync(*TABLES)


def teardown() -> None:
    drop_db_tables_sync(*TABLES)


@pytest_asyncio.fixture(autouse=True)
def setup_teardown() -> Generator:
    setup()
    yield
    teardown()
