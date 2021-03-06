import logging

from aiogram.types.message import Message

import config
import database
from dispatcher import bot


async def cleaner_body(message: Message, message_user: Message = None) -> None:
    """
    Всё в одну функцию
    :param: Тело сообщения
    :return:
    """
    if config.CLEANER:
        try:
            data = database.PostSQL_ChatManager(message).get_last_message
            database.PostSQL_ChatManager(message, message_user).modify_last
            await bot.delete_message(data["chat_id"], data["last_message_id"])
            if message_user:
                try:
                    await bot.delete_message(data["chat_id"], data["last_user_message_id"])
                except Exception as e:
                    logging.debug("Error deleting message user in group %d. User msg: %d" % (
                        data["chat_id"], data["last_user_message_id"]))
        except Exception as e:
            try:
                database.PostSQL_ChatManager(message, message_user).add_new_chat
            except:
                pass
            logging.debug("Body cleaner error. Details: %s" % e)
