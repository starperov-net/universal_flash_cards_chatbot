from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.storages import TmpStorage
from redis import Redis

from app.settings import settings

redis = Redis(host="redis")
#storage = RedisStorage(redis=redis)  # type: ignore
storage = MemoryStorage()
tmp_storage = TmpStorage()
bot = Bot(token=settings.BOT_TOKEN)  # type: ignore
dp = Dispatcher(storage=storage, tmp_storage=tmp_storage)
