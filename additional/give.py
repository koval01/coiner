import logging
from aiogram.types.message import Message

import database
from special.utils import Utils
from config import SLAVES_PAY_NOTIFY


async def init_give(message: Message = None,
                    sum_: int = 0, user_: int = 0,
                    custom_name: str = None,
                    item_sell: bool = False,
                    slaves_mode: bool = False) -> None:
    """
    Функция для выдачи гривен
    :param message: Тело сообщения
    :param sum_: Сумма
    :param user_: Получатель
    :param custom_name: Кастомное имя отправителя
    :param item_sell: Режим продажи предмета
    :return:
    """
    if message:
        name_ = await Utils().get_name_(message)
    else:
        name_ = custom_name

    if not user_:
        user_ = message.from_user.id

    try:
        database.PostSQL(message).modify_balance(
            sum_, custom_user=user_,
        )
    except Exception as e:
        logging.error(e)
        return

    # Уведомим получателя
    if not item_sell:
        if slaves_mode and not SLAVES_PAY_NOTIFY:
            return
        await Utils().notify_("На счёт было зачислено <b>%d</b> гривен от <b>%s</b>" % (
            sum_, name_
        ), user_, need_delete=slaves_mode)

    return
