from aiogram.utils.exceptions import Throttled
from aiogram.types.message import Message
from dispatcher import dp


async def throttling_all(msg: Message) -> bool:
    try:
        await dp.throttle('throttle_all', rate=0.7)
    except Throttled:
        await msg.reply("Не флуди пожалуйста!")
        return False
    else:
        return True