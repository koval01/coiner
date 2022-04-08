import logging

from aiogram.types.message import Message

import config
import database
from dispatcher import bot


async def cleaner_body(message: Message) -> None:
    """
    Всё в одну функцию
    :param: Тело сообщения
    :return:
    """
    if config.CLEANER:
        try:
            data = database.PostSQL_ChatManager(message).get_last_message
            database.PostSQL_ChatManager(message).modify_last
            await bot.delete_message(data[0], data[1])
        except Exception as e:
            database.PostSQL_ChatManager(message).add_new_chat
            logging.error(e)
