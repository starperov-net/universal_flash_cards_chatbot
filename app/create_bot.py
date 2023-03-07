from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.storages import TmpStorage

from app.settings import settings

storage = MemoryStorage()
tmp_storage = TmpStorage()
bot = Bot(token=settings.BOT_TOKEN)  # type: ignore
dp = Dispatcher(storage=storage, tmp_storage=tmp_storage)
