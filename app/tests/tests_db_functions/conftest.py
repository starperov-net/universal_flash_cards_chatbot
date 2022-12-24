import pytest_asyncio
from piccolo.table import create_db_tables_sync, drop_db_tables_sync

from app.tables import User, Context, Item
from app.tests.tests_db_functions.test_db_function_personal import TABLES
from app.tests.utils import TABLE_USER_1, CONTEXT_UK, CONTEXT_EN, ITEM_UK, ITEM_EN


@pytest_asyncio.fixture
async def user():
    await User.insert(TABLE_USER_1)
    return TABLE_USER_1


@pytest_asyncio.fixture
async def context_uk():
    await Context.insert(CONTEXT_UK)
    return CONTEXT_UK


@pytest_asyncio.fixture
async def context_en():
    await Context.insert(CONTEXT_EN)
    return CONTEXT_EN


@pytest_asyncio.fixture
async def item_uk(user, context_uk):
    await Item.insert(ITEM_UK)
    return ITEM_UK


@pytest_asyncio.fixture
async def item_en(user, context_en):
    await Item.insert(ITEM_EN)
    return ITEM_EN


def setup():
    create_db_tables_sync(*TABLES)


def teardown():
    drop_db_tables_sync(*TABLES)


@pytest_asyncio.fixture(autouse=True)
def setup_teardown():
    setup()
    yield
    teardown()
