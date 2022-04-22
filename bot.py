import asyncio
import logging

from aiogram import executor

from dispatcher import dp
from special.slaves_sc import SchedulerSlaves
from special.throttling import ThrottlingMiddleware

import handlers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(SchedulerSlaves().scheduler())
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)
