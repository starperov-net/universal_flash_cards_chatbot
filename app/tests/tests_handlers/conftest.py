import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from app.tests.tests_handlers.mocked_bot import MockedBot
from app.tests.tests_handlers.utils import TEST_USER_CHAT
from app.tests.utils import TELEGRAM_USER_1 as TEST_USER


@pytest_asyncio.fixture(scope="session")
async def storage() -> AsyncGenerator:
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest_asyncio.fixture(scope="session")
def bot() -> Generator:
    bot = MockedBot()
    token = Bot.set_current(bot)
    try:
        yield bot
    finally:
        Bot.reset_current(token)


@pytest_asyncio.fixture()
async def dispatcher() -> AsyncGenerator:
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def state(bot: MockedBot, storage: MemoryStorage) -> FSMContext:

    return FSMContext(
        bot=bot,
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id),
    )
