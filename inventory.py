import logging
from aiogram.types.message import Message
import database


async def give_item(message: Message, item_id: int) -> bool:
    """
    Выдача предмета
    :param message: Тело сообщения
    :param item_id: Айди предмета который нужно выдать
    :return: Success bool
    """
    if len(database.PostSQL_Inventory(message).get_inventory()) < 50:
        try:
            database.PostSQL_Inventory(message).give_item(item_id)
            return True
        except Exception as e:
            await message.reply("Не удалось выдать предмет через ошибку базы данных!")
            logging.error(e)
    else:
        await message.reply("У тебя максимум предметов, продай что-то")
        return False


async def take_item(message: Message, item_id: int) -> bool:
    """
    Отбирание предмета
    :param message: Тело сообщения
    :param item_id: Айди предмета который нужно выдать
    :return: Success bool
    """
    if len(database.PostSQL_Inventory(message).get_inventory()) != 0:
        try:
            database.PostSQL_Inventory(message).take_item(item_id)
            return True
        except Exception as e:
            await message.reply("Не удалось отобрать предмет через ошибку базы данных!")
            logging.error(e)
    else:
        await message.reply("Произошла ошибка!")
        return False
