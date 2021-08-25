import database
import logging

from aiogram.types.message import Message

from utils import get_name_, notify_


async def init_give(message: Message, sum_: int, user_: int) -> None:
    """
    Функция для выдачи монет
    :param message: Тело сообщения
    :param sum_: Сумма
    :param user_: Получатель
    :return:
    """
    name_ = await get_name_(message)

    try:
        database.PostSQL(message).modify_balance(
            sum_, custom_user=user_,
        )
    except Exception as e:
        logging.error(e)
        return

    # Уведомим получателя
    await notify_("На счёт было зачислено %d COINS от %s" % (
                sum_, name_
            ), user_)

    return True


