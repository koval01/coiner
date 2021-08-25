from aiogram.types.message import Message
from dispatcher import bot
import logging


async def get_name_(message: Message) -> str:
    """
    Получаем имя пользователя
    :param message: Тело сообщения
    :return: Строка с именем пользователя
    """
    name_ = "Неизвестный"
    try:
        try:
            name_ = message.chat.title
        except Exception as e:
            logging.debug(e)
        if not name_:
            try:
                name_ = message.from_user.full_name
            except Exception as e:
                logging.debug(e)
    except Exception as e:
        logging.warning(e)

    return name_


async def notify_(text_: str, user_: int) -> bool:
    """
    Отправка уведомления
    :param text_: Текст
    :param user_: ID юзера
    :return: Результат отправки, успешно или нет
    """
    try:
        await bot.send_message(
            user_, text_,
        )
        return True
    except Exception as e:
        logging.warning(e)
        return False