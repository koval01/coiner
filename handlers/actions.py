import logging
from random import uniform, randint

from aiogram import types
from aiogram.types.message import Message

import config
import database
from dispatcher import dp
from give import init_give
from pay import init_pay
from throttling import throttling_all
from .cleaner import cleaner_body
from utils import human_format


# Глобальная функция для создания счёта юзера
async def private_balance_create(message: Message, pass_check=False, cust_usr=0) -> None:
    if database.PostSQL(message).check_user():
        if not pass_check:
            await message.reply("Твой баланс: %d гривен" % database.PostSQL(message).get_balance(
                custom_user=cust_usr))
    else:
        database.PostSQL(message).add_user(custom_user=cust_usr)
        database.PostSQL(message).modify_balance(config.START_BALANCE, custom_user=cust_usr)
        await message.reply("Привет %s, твой счёт успешно создан. Также тебе было начислено %d гривен!" % (
            message.from_user.first_name, config.START_BALANCE
        ))
            

# Создание счёта, доступно тоже для всех
@dp.message_handler(commands=['start'], is_private=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        private_balance_create(message)


@dp.message_handler(commands=['start'], is_group=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        if database.PostSQL(message).check_user():
            await message.reply("Баланс этой группы: %d гривен" % database.PostSQL(message).get_balance())
        else:
            database.PostSQL(message).add_user()
            database.PostSQL(message).modify_balance(config.START_BALANCE)
            await message.reply(
                "Счёт группы успешно создан. Также на баланс группы было начислено %d гривен!" %
                config.START_BALANCE
            )


# Проверка баланса, работает без всяких ограничений
@dp.message_handler(commands=['wallet'], is_private=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).check_user()
        await message.reply("Твой баланс: %d гривен\nНомер счёта: «%d»" % (data[2], data[3]))


# И команда для групп конечно
@dp.message_handler(commands=['wallet'], is_group=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).check_user()
        bot_msg = await message.reply("Баланс группы: %d гривен\nНомер счёта группы: «%d»" % (data[2], data[3]))
        await cleaner_body(bot_msg)


# Если вызвали из приватного чата
@dp.message_handler(commands=['pay'], is_private=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        try:
            u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
            if u_ == message.chat.id:
                await message.reply("Какое-то странное действие.")
                return
            x = await init_pay(message, s_, u_)
            if x:
                await message.reply("Получатель: %d\nСумма: %d" % (
                    u_, s_
                ))
        except Exception as e:
            logging.debug(e)
            await message.reply("/pay *получатель* *сумма*")


# Если вызвал админ из группы
@dp.message_handler(commands=['pay'], is_admin=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        try:
            u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
            if u_ == message.chat.id:
                await message.reply("Какое-то странное действие.")
                return
            x = await init_pay(message, s_, u_)
            if x:
                await message.reply("Получатель: %d\nСумма: %d" % (
                    u_, s_
                ))
        except Exception as e:
            logging.debug(e)
            await message.reply("/pay *получатель* *сумма*")


# Если вызвал участник группы, без прав администратора
@dp.message_handler(commands=['pay'], is_admin=False)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        await message.reply("Чтобы управлять счётом, нужно быть администратором группы.")


# Выдача монет от владельца бота
@dp.message_handler(commands=['give'], is_owner=True)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        try:
            u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
            data = database.PostSQL(message).check_user(custom_user=u_)
            x = await init_give(message, s_, u_)
            if x:
                await message.reply("Для %s было выдано %d гривен!" % (
                    data[1], s_
                ))
        except Exception as e:
            logging.debug(e)
            await message.reply("/give *получатель* *сумма*")


# Если у пользователя нет прав на эту команду
@dp.message_handler(commands=['give'], is_owner=False)
async def check_balance(message: types.Message):
    if await throttling_all(message):
        await message.reply("Недоступно!")


# Немного информации о боте
@dp.message_handler(commands=['info'])
async def check_balance(message: types.Message):
    if await throttling_all(message):
        await message.reply(config.BOT_INFO)


# Ну и подсказки по боту
@dp.message_handler(commands=['faq'])
async def check_balance(message: types.Message):
    if await throttling_all(message):
        await message.reply(config.BOT_FAQ)


# Испытаем удачу
@dp.message_handler(commands=['dice'])
async def check_balance(message: types.Message):
    if await throttling_all(message):
        if uniform(0, 1) >= 0.4:
            value_ = randint(1, 10) + (randint(30, 200) / uniform(2, 5))
            database.PostSQL(message).modify_balance(value_, custom_user=message.from_user.id)
            bot_msg = await message.reply("Тебе выпало %d гривен!" % value_)
        else:
            bot_msg = await message.reply("Тебе не повезло. Ничего не выпало... :(")
        await cleaner_body(bot_msg)


# Добавим и возможноть посмотреть кто там самый богатый
@dp.message_handler(commands=['top'])
async def check_balance(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).get_top_balance()
        top_ = "\n".join(
            ["<b>%d.</b> <i>%s</i> <b>-</b> <code>%s</code> <b>гривен</b>" %
            (i+1, e[0], human_format(int(e[1]))) for i, e in enumerate(data)]
        )
        bot_msg = await message.reply(top_)
        await cleaner_body(bot_msg)


# Слушаем группу, и выдаём для группы вознаграждение за актив
@dp.message_handler(is_group=True)
async def group_echo(message: types.Message):
    private_balance_create(message, pass_check=True, cust_usr=message.from_user.id)
    
    if uniform(0, 1) >= 0.95:
        value_ = randint(1, 20)
        value_for_user = randint(1, 5)

        database.PostSQL(message).modify_balance(value_)

        try:
            database.PostSQL(message).modify_balance(
                value_for_user, custom_user=message.from_user.id,
            )
            await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - %d гривен"
                "\nТакже случайному участнику %s - %d гривен" %
                (value_, message.from_user.full_name, value_for_user)
            )
        except Exception as e:
            logging.error(e)
            await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - %d гривен" % value_
            )


