from aiogram import executor
from dispatcher import dp
import slaves_sc
import handlers
import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(slaves_sc.scheduler())
    executor.start_polling(dp, skip_updates=True)

