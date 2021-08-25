from aiogram.utils.exceptions import Throttled
from aiogram.types.message import Message
from dispatcher import dp


async def throttling_all(msg: Message) -> bool:
    try:
        await dp.throttle('throttle_all', rate=0.4)
    except Throttled:
        return False
    else:
        return True
