import logging
from aiogram.types.message import Message

from dispatcher import bot
import database
import config
import re


class Utils:
    def __init__(self) -> None:
        pass

    async def get_name_(self, message: Message) -> str:
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

    async def cleaner_slaves_notify(self, message: Message) -> None:
        if config.CLEANER:
            try:
                data = database.PostSQL(message).get_last_slaves_message
                database.PostSQL(message).modify_last_msg_slaves
                await bot.delete_message(data["user_id"], data["slaves_last_msg"])
            except Exception as e:
                logging.warning("Error in cleaner slaves notify: %s" % e)

    async def notify_(self, text_: str, user_: int, need_delete: bool = False) -> bool:
        if need_delete:
            pass
        try:
            bot_msg = await bot.send_message(
                user_, text_,
            )
            await self.cleaner_slaves_notify(bot_msg)
            return True
        except Exception as e:
            logging.warning(e)
            return False

    def human_format(self, num: int) -> str:
        num = float('{:.3g}'.format(num))
        magnitude = 0

        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        return '{}{}'.format(
            '{:f}'.format(num).rstrip('0').rstrip('.'),
            ['', 'K', 'M', 'B', 'T', 'Q'][magnitude]
        )

    def number_to_words(self, number: int) -> str:
        x = {1: 'одна', 2: 'две', 3: 'три', 4: 'четыре', 5: 'пять',
             6: 'шесть', 7: 'семь', 8: 'восемь', 9: 'девять'}
        y = {10: 'десять', 20: 'двадцать', 30: 'тридцать', 40: 'сорок',
             50: 'пятьдесят', 60: 'шестьдесят', 70: 'семьдесят',
             80: 'восемьдесят', 90: 'девяносто'}
        b = {11: 'одиннадцать', 12: 'двенадцать', 13: 'тринадцать',
             14: 'четырнадцать', 15: 'пятнадцать', 16: 'шестнадцать',
             17: 'семнадцать', 18: 'восемнадцать', 19: 'девятнадцать'}

        number_1 = number % 10
        number_2 = number - number_1

        if number < 10:
            return x.get(number)
        elif number >= 10 and number_2 == 0:
            return y.get(number)
        elif number > 20:
            return y.get(number_2) + ' ' + x.get(number_1)
        elif 10 < number < 20:
            return b.get(number)
        else:
            return 'Число вне диапазона среза!'

    def cleaner_name(self, name: str) -> str:
        if len(name) >= 24:
            name = name[:24]
        if len(name) != 0:
            return name
        else:
            return "🤷‍♂️"

    def get_text_for_news_command(self, full_text: str) -> str:
        pattern = re.compile(r"(?P<command>\/[A-Za-z_@]*?)\s(?P<text>[\W\S]*)")
        return re.search(pattern, full_text).group("text")
