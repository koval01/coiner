from aiogram.utils.exceptions import Throttled
from aiogram.types.message import Message
from dispatcher import dp
# from handlers.actions import private_balance_create


async def throttling_all(msg: Message) -> bool:
    try:
        await dp.throttle('throttle_all', rate=0.4)
    except Throttled:
        return False
    else:
        # await private_balance_create(
        #     msg, pass_check=True, cust_usr=msg.from_user.id)
        return True
