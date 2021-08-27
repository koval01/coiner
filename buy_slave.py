from aiogram.types.message import Message
import logging
import database
import config


async def init_transaction_(message: Message) -> None:
    """
    Функция для покупки раба
    :param message: Тело сообщения
    :return:
    """
    slaves_count = database.PostSQL(message).get_slaves()
    if slaves_count:
        slave_price = slaves_count * config.SLAVE_PRICE_PRC * config.SLAVE_PRICE
    else:
        slave_price = config.SLAVE_PRICE

    try:
        if int(database.PostSQL(message).check_user()[2]) < slave_price:
            await message.reply("Недостаточно гривен! Новый раб стоит %d гривен!" % slave_price)
            return

        # Сначала пробуем снять монеты со счёта покупателя
        try:
            database.PostSQL(message).modify_balance(
                slave_price, take=True,
            )
        except Exception as e:
            logging.error(e)
            return

        # Если получилось снять, то теперь пробуем зачислить на счёт нового раба
        try:
            database.PostSQL(message).modify_slaves()
        except Exception as e:
            logging.error(e)
            return

    except Exception as e:
        await message.reply("Что-то пошло не так")
        logging.warning(e)
        return

    return True


