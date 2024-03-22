from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from config import BOT_TOKEN

job_stores = {
    "default": RedisJobStore(
        jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
        host="localhost", port=6379
    )
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
storage = MemoryStorage()
bot = Bot(BOT_TOKEN)  # testing
dp = Dispatcher(bot, storage=storage)
scheduler.start()
