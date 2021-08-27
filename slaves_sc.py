import asyncio
import aioschedule as schedule
from dispatcher import bot


async def slaves_() -> None:
    pass


async def scheduler():
    schedule.every(10).minutes.do(slaves_)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


