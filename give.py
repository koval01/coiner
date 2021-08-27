import logging
from aiogram.types.message import Message

import database
from utils import get_name_, notify_


async def init_give(message: Message = None,
                    sum_: int = 0, user_: int = 0,
                    custom_name: str = None) -> None:
    """
    Функция для выдачи гривен
    :param message: Тело сообщения
    :param sum_: Сумма
    :param user_: Получатель
    :param custom_name: Кастомное имя отправителя
    :return:
    """
    if message:
        name_ = await get_name_(message)
    else:
        name_ = custom_name

    try:
        database.PostSQL(message).modify_balance(
            sum_, custom_user=user_,
        )
    except Exception as e:
        logging.error(e)
        return

    # Уведомим получателя
    await notify_("На счёт было зачислено %d гривен от %s" % (
        sum_, name_
    ), user_)

    return True
