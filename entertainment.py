from aiogram.types.message import Message
from random import uniform, choice
import logging


async def ask_(message: Message) -> None:
    try:
        if message.text[-1:] == "?":
            r_ = choice(["отрицательного", "утвердительного"])
            await message.reply(
                "<i>Шанс </i><b>%s</b><i> ответа на </i>«<b>%s</b>»<i>, примерно </i><b>%f%%</b>" % (
                    r_, message.text, uniform(0, 100)
                )
            )
    except Exception as e:
        logging.warning(e)

