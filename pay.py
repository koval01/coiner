from aiogram.types.message import Message
from utils import get_name_, notify_
import logging, database


async def init_pay(message: Message, sum_: int, user_: int) -> None:
    """
    Функция для передачи монет
    :param message: Тело сообщения
    :param sum_: Сумма
    :param user_: Получатель
    :return:
    """
    name_ = await get_name_(message)

    try:
        if not database.PostSQL(message).check_user(custom_user=user_):
            await message.reply("Ошибка, не удалось найти получателя.")
            return

        if int(database.PostSQL(message).check_user()[2]) < sum_:
            await message.reply("Недостаточно монет!")
            return

        # Сначала пробуем снять монеты со счёта отправителя
        try:
            database.PostSQL(message).modify_balance(
                sum_, take=True,
            )
        except Exception as e:
            logging.error(e)
            return

        # Если получилось снять, то теперь пробуем зачислить
        try:
            database.PostSQL(message).modify_balance(
                sum_, custom_user=user_,
            )
        except Exception as e:
            logging.error(e)
            return

        # Уведомим получателя
        await notify_("На счёт было зачислено %d COINS от %s" % (
            sum_, name_
        ), user_)

    except Exception as e:
        await message.reply("Что-то пошло не так, проверьте правильно лы всё ввели"
                            " и убедитесь - существует ли получатель.")
        logging.warning(e)
        return

    return True
