import asyncio

from aiogram import executor

import slaves_sc
import handlers
from dispatcher import dp
from throttling import ThrottlingMiddleware

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(slaves_sc.scheduler())
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)
