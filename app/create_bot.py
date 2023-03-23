from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from app.storages import TmpStorage
from redis.asyncio import Redis

from app.settings import settings


redis = Redis(host="redis")
storage = RedisStorage(redis=redis)  # type: ignore
tmp_storage = TmpStorage()
bot = Bot(token=settings.BOT_TOKEN)  # type: ignore
dp = Dispatcher(storage=storage, tmp_storage=tmp_storage)
