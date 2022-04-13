import asyncio

import aioschedule as schedule

import config
import database
from additional.give import init_give


async def slaves_() -> None:
    owners = database.PostSQL().get_slave_owners
    for i in owners:
        data = int(database.PostSQL().get_slaves(
            custom_user=i["user_id"]))
        add_ = data * config.PAY_PER_SLAVE
        await init_give(
            None, sum_=add_, custom_name="рабы",
            user_=i["user_id"], slaves_mode=True
        )


async def scheduler():
    await slaves_()
    schedule.every().hour.do(slaves_)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
