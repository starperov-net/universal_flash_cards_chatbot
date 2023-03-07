from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from app.storages import TmpStorage
from aioredis import Redis

from app.settings import settings

redis = Redis(host='redis')


#storage = MemoryStorage()
storage = RedisStorage(redis=redis)
tmp_storage = TmpStorage()
bot = Bot(token=settings.BOT_TOKEN)  # type: ignore
dp = Dispatcher(storage=storage, tmp_storage=tmp_storage)
