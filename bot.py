import asyncio
from aiogram import executor

import handlers
import slaves_sc
from dispatcher import dp

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(slaves_sc.scheduler())
    executor.start_polling(dp, skip_updates=True)
