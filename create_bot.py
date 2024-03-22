from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

job_stores = {
    "default": RedisJobStore(
        jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
        host="localhost", port=6379
    )
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))
storage = MemoryStorage()
bot = Bot('7123990335:AAEoZvtOYB3H-U1AaYh8C9mIwNTyB45O8Mk')  # testing
dp = Dispatcher(bot, storage=storage)
scheduler.start()
