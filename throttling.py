from aiogram.types.message import Message
from aiogram.utils.exceptions import Throttled

import handlers
from dispatcher import dp


async def throttling_(msg: Message, throttle_name: str = "throttle_all",
                      rate: int = 0.3) -> bool:
    try:
        await dp.throttle(throttle_name, rate=rate)
    except Throttled:
        return False
    else:
        await handlers.actions.private_balance_create(
            msg, pass_check=True, cust_usr=msg.from_user.id)
        return True
