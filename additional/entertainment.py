import logging
from random import uniform, choice

from aiogram.types.message import Message

import config
from additional.inventory import give_item
from additional.items import items_ as all_items
from handlers.cleaner import cleaner_body


async def ask_(message: Message) -> None:
    """
    Вопрос юзера
    :param message: Тело сообщения
    :return:
    """
    try:
        if message.text[-1:] == message.text[:1] == "?" and len(message.text) >= 5:
            r_ = choice(["отрицательного", "утвердительного"])
            bot_msg = await message.reply(
                "<i>Шанс </i><b>%s</b><i> ответа на </i>«<b>%s</b>»<i>, примерно </i><b>%f%%</b>" % (
                    r_, message.text[1:], uniform(0, 100)
                )
            )
            await cleaner_body(bot_msg, message)
    except Exception as e:
        logging.warning(e)


async def fagot_(message: Message) -> None:
    """
    Чек на пидора
    :param message: Тело сообщения
    :return:
    """
    value_ = uniform(0, 100)
    if int(config.BOT_OWNER) == int(message.from_user.id):
        value_ = float(0)

    try:
        bot_msg = await message.reply(
            "<i>Шанс что ты пидор примерно </i><b>%f%%</b>" % (
                value_,
            )
        )
        if value_ > 50:
            item__ = choice([86, 87, 88])
            item_ = all_items[item__]
            try:
                await give_item(message, item__)
                await message.reply("Тебе выпало %s %s (стоимость %d гривен)" % (
                    item_['icon'], item_['name'], item_['price']
                ))
            except Exception as e:
                logging.warning(e)
        await cleaner_body(bot_msg, message)
    except Exception as e:
        logging.warning(e)
