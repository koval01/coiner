import logging
from aiogram.types.message import Message
from items import items_ as all_items
from random import uniform, choice, shuffle
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
            await message.reply("Не удалось выдать предмет через <b>ошибку базы данных</b>!")
            logging.error(e)
    else:
        await message.reply(
            "У тебя максимум предметов, продай что-то."
            " Продать что-то конкретное <b>/sell *ID предмета*</b>"
            " или продать весь инвентарь <b>/sellall</b>"
        )
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
            await message.reply("Не удалось отобрать предмет через <b>ошибку базы данных</b>!")
            logging.error(e)
    else:
        await message.reply("Произошла ошибка!")
        return False


async def take_all_items(message: Message) -> bool:
    """
    Отбирание всех предметов у пользователя
    :param message: Тело сообщения
    :return: Success bool
    """
    if len(database.PostSQL_Inventory(message).get_inventory()) != 0:
        try:
            database.PostSQL_Inventory(message).clear_inventory()
            return True
        except Exception as e:
            await message.reply("Не удалось отобрать предметы через <b>ошибку базы данных</b>!")
            logging.error(e)
    else:
        await message.reply("Произошла ошибка!")
        return False


async def item_dice() -> dict:
    """
    Рулетка на вещи
    :return: Словарь с данными о выигранной вещи
    """
    local_items_ = all_items[:]
    shuffle(local_items_)
    for i in range(100):
        for i in local_items_:
            if i["chance_drop"] > uniform(0, 1) > uniform(0, 0.9):
                return i

    return choice([i for i in local_items_ if i["chance_drop"] > 0.7])
