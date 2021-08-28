import logging
from aiogram.types.message import Message
from items import items_ as all_items
from random import uniform, choice
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


async def item_dice() -> dict:
    """
    Рулетка на вещи
    :return: Словарь с данными о выигранной вещи
    """
    for i in range(50):
        for i in all_items:
            if i["chance_drop"] > uniform(0, 1) > uniform(0, 0.9):
                return i

    return choice([i for i in all_items if i["chance_drop"] > 0.7])
