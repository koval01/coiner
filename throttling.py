from aiogram.utils.exceptions import Throttled
from aiogram.types.message import Message
from dispatcher import dp
import handlers


async def throttling_all(msg: Message) -> bool:
    try:
        await dp.throttle('throttle_all', rate=0.4)
    except Throttled:
        return False
    else:
        await handlers.actions.private_balance_create(
            msg, pass_check=True, cust_usr=msg.from_user.id)
        return True
