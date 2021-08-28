from aiogram.types.message import Message
from random import uniform, choice
from throttling import throttling_
import logging


async def ask_(message: Message) -> None:
    """
    Вопрос юзера
    :param message: Тело сообщения
    :return:
    """
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


async def fagot_(message: Message) -> None:
    """
    Чек на пидора
    :param message: Тело сообщения
    :return:
    """
    if await throttling_(
            message,
            throttle_name="fagot_info",
            rate=900
    ):
        try:
            await message.reply(
                "<i>Шанс что ты пидор примерно </i><b>%f%%</b>" % (
                    uniform(0, 100)
                )
            )
        except Exception as e:
            logging.warning(e)
    else:
        await message.reply("Я ещё думаю на счёт тебя...")

