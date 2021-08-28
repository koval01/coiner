from aiogram.types.message import Message
from random import uniform, choice
from throttling import throttling_
import logging
import config


async def ask_(message: Message) -> None:
    """
    Вопрос юзера
    :param message: Тело сообщения
    :return:
    """
    try:
        if message.text[-1:] == message.text[:1] == "?" and len(message.text) >= 5:
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
        value_ = uniform(0, 100)
        if int(config.BOT_OWNER) == int(message.from_user.id):
            value_ = float(0)

        try:
            await message.reply(
                "<i>Шанс что ты пидор примерно </i><b>%f%%</b>" % (
                    value_,
                )
            )
        except Exception as e:
            logging.warning(e)
    else:
        await message.reply("Я ещё думаю на счёт тебя...")

