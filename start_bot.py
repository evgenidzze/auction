import logging

from aiogram.utils import executor

from db_manage import on_startup
from handlers.admin import register_admin_handlers
from handlers.client import register_client_handlers
from create_bot import dp
# from db_manage import on_startup | connect db on_startup=on_startup

register_client_handlers(dp)
register_admin_handlers(dp)
logging.basicConfig(level=logging.INFO, filename='logs.log')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

executor.start_polling(dispatcher=dp, on_startup=on_startup, skip_updates=True)
