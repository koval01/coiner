import logging

from aiogram import types
from dispatcher import dp
from random import uniform, randint
from pay import init_pay
from aiogram.utils.exceptions import Throttled
from give import init_give
import config, database


# Создание счёта, доступно тоже для всех
@dp.message_handler(commands=['start'], is_private=True)
async def check_balance(message: types.Message):
    try:
        await dp.throttle('throttle_all', rate=2)
    except Throttled:
        await message.reply('Too many requests!')
    else:
        if database.PostSQL(message).check_user():
            await message.reply("Твой баланс: %d COINS" % database.PostSQL(message).get_balance())
        else:
            database.PostSQL(message).add_user()
            database.PostSQL(message).modify_balance(config.START_BALANCE)
            await message.reply("Привет %s, твой счёт успешно создан. Также тебе было начислено %d COINS!" % (
                message.from_user.first_name, config.START_BALANCE
            ))


@dp.message_handler(commands=['start'], is_group=True)
async def check_balance(message: types.Message):
    if database.PostSQL(message).check_user():
        await message.reply("Баланс группы: %d COINS" % database.PostSQL(message).get_balance())
    else:
        database.PostSQL(message).add_user()
        database.PostSQL(message).modify_balance(config.START_BALANCE)
        await message.reply(
            "Счёт группы успешно создан. Также на баланс группы было начислено %d COINS!" %
            config.START_BALANCE
        )


# Проверка баланса, работает без всяких ограничений
@dp.message_handler(commands=['wallet'])
async def check_balance(message: types.Message):
    data = database.PostSQL(message).check_user()
    await message.reply("Твой баланс: %d COINS\nНомер счёта: «%d»" % (data[2], data[3]))


# Если вызвали из приватного чата
@dp.message_handler(commands=['pay'], is_private=True)
async def check_balance(message: types.Message):
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
    await message.reply("Чтобы управлять счётом, нужно быть администратором группы.")


# Выдача монет от владельца бота
@dp.message_handler(commands=['give'], is_owner=True)
async def check_balance(message: types.Message):
    u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
    data = database.PostSQL(message).check_user(custom_user=u_)
    x = await init_give(message, s_, u_)
    if x:
        await message.reply("Для %s было выдано %d COINS!" % (
            data[1], s_
        ))


# Если у пользователя нет прав на эту команду
@dp.message_handler(commands=['give'], is_owner=False)
async def check_balance(message: types.Message):
    await message.reply("Недоступно!")


# Немного информации о боте
@dp.message_handler(commands=['info'])
async def check_balance(message: types.Message):
    await message.reply(config.BOT_INFO)


# Слушаем группу, и выдаём для группы вознаграждение за актив
@dp.message_handler(is_group=True)
async def group_echo(message: types.Message):
    if uniform(0, 1) >= 0.95:
        value_ = randint(1, 20)
        database.PostSQL(message).modify_balance(value_)
        await message.answer(
            "За активность в этой группе на баланс было зачисленно - %d COINS" %
            value_
        )