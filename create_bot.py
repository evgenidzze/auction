import asyncio
from pathlib import Path
import aioredis
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram_media_group.storages.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from utils.config import BOT_TOKEN, REDIS_HOST
from handlers.middleware import Localization, MyBot


def async_to_sync(awaitable):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)


job_stores = {
    "default": RedisJobStore(db=0,
                             jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
                             host=REDIS_HOST, port=6379
                             )
}

I18N_DOMAIN = 'auction'
BASE_DIR = Path(__file__).parent

LOCALES_DIR = BASE_DIR / 'locales'

i18n = Localization(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext
scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
storage = RedisStorage2(host=REDIS_HOST)
connection = async_to_sync(aioredis.create_connection(f'redis://{REDIS_HOST}/0'))
storage_group = RedisStorage(connection, "aiogram_media_group", 2)
bot = MyBot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
scheduler.start()
