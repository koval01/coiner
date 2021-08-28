import logging
from aiogram import types
from aiogram.types.message import Message
from random import uniform, randint

import config
import database
from buy_slave import init_transaction_ as slave_buy_
from dispatcher import dp
from give import init_give
from pay import init_pay
from items import items_ as all_items
from inventory import take_item, item_dice, give_item, take_all_items
from entertainment import ask_, fagot_
from throttling import throttling_ as throttling_all
from utils import human_format
from .cleaner import cleaner_body


# Глобальная функция для создания счёта юзера
async def private_balance_create(message: Message, pass_check=False, cust_usr=0) -> None:
    data = database.PostSQL(message, set_private=pass_check).check_user(custom_user=cust_usr)
    if data:
        try:
            if message.from_user.full_name and \
                    message.from_user.full_name != data[1]:
                database.PostSQL(message).modify_name_(
                    name=message.from_user.full_name)
        except Exception as e:
            logging.debug(e)

        try:
            if message.chat.title and \
                    message.chat.title != data[1]:
                database.PostSQL(message).modify_name_(
                    name=message.chat.title)
        except Exception as e:
            logging.debug(e)

        if not pass_check:
            await message.reply("Твой баланс: %d гривен" % database.PostSQL(
                message, set_private=pass_check
            ).get_balance(
                custom_user=cust_usr
            ))
    else:
        database.PostSQL(message, set_private=pass_check).add_user(custom_user=cust_usr)
        database.PostSQL(message, set_private=pass_check).modify_balance(config.START_BALANCE, custom_user=cust_usr)
        await message.reply("Привет %s, твой счёт успешно создан. Также тебе было начислено %d гривен!" % (
            message.from_user.first_name, config.START_BALANCE
        ))


# Создание счёта, доступно тоже для всех
@dp.message_handler(commands=['start'], is_private=True)
async def start_for_private(message: types.Message):
    if await throttling_all(message):
        await private_balance_create(message)


@dp.message_handler(commands=['start'], is_group=True)
async def start_for_group(message: types.Message):
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
async def wallet_private(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).check_user()
        await message.reply("Твой баланс: %d гривен\nНомер счёта: «%d»" % (data[2], data[3]))


# И команда для групп конечно
@dp.message_handler(commands=['wallet'], is_group=True)
async def wallet_group(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).check_user()
        bot_msg = await message.reply("Баланс группы: %d гривен\nНомер счёта группы: «%d»" % (data[2], data[3]))
        await cleaner_body(bot_msg)


# Если вызвали из приватного чата
@dp.message_handler(commands=['pay'], is_private=True)
async def pay_in_private(message: types.Message):
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


@dp.message_handler(commands=['buyslave'])
async def buy_slave_private(message: types.Message):
    if await throttling_all(message):
        try:
            x = await slave_buy_(message)
            if x:
                await message.reply("Ты успешно купил нового раба >:)")
        except Exception as e:
            logging.debug(e)


@dp.message_handler(commands=['slaves'])
async def user_slaves(message: types.Message):
    if await throttling_all(message):
        data = int(database.PostSQL(message).get_slaves(
            custom_user=message.from_user.id))
        await message.reply("У тебя %d рабов\nДоход с них %d гривен в час" % (
            data, data * config.PAY_PER_SLAVE
        ))


# Можно даже глянуть свой инвентарь
@dp.message_handler(commands=['inventory'])
async def user_inventory(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL_Inventory(message).get_inventory()
        items_ = "\n".join(
            ["(%d) %s %s (%d гривен)" %
             (
                i[1],
                all_items[i[0]]["icon"],
                all_items[i[0]]["name"],
                all_items[i[0]]["price"]
             ) for i in data]
        )
        bot_msg = await message.reply("%s\n\nСлотов занято: <b>%d/50</b>" % (items_, len(data)))
        await cleaner_body(bot_msg)


# Продажа предметов
@dp.message_handler(commands=['sell'])
async def sell__(message: types.Message):
    if await throttling_all(message):
        try:
            item_id = int(message.text.split()[1])
            data_ = database.PostSQL_Inventory(message).get_item(item_id)
            if int(data_[2]) != message.from_user.id:
                await message.reply("Мне кажется или этот предмет не твой"
                                    "\nТы меня обмануть решил что ли? Гадёныш, "
                                    "иди делом лучше займись!")
                return

            x = await take_item(message, item_id)
            item__ = all_items[int(data_[0])]
            item_price = item__["price"]
            if x:
                await init_give(message, item_price, item_sell=True)
                await message.reply("Предмет %s %s был продан за %d гривен!" % (
                    item__["icon"], item__["name"], item_price
                ))
        except Exception as e:
            logging.info(e)
            await message.reply(
                "/sell *ID предмета*"
                "\n\nПример: (*ID предмета*) 🇺🇸 "
                "Флаг США (15000 гривен)"
            )


# Продажа всего инвентаря сразу
@dp.message_handler(commands=['sellall'])
async def sell_all_items(message: types.Message):
    if await throttling_all(message):
        try:
            items_price = sum([all_items[el[0]]["price"] for el in database.PostSQL_Inventory(message).get_inventory()])
            x = await take_all_items(message)
            if x:
                await init_give(message, items_price, item_sell=True)
                await message.reply("Предметы были проданы за %s гривен!" % human_format(items_price))
        except Exception as e:
            logging.info(e)
            await message.reply("Произошла ошибка, похоже что у тебя нет предметов.")


# Если вызвал админ из группы
@dp.message_handler(commands=['pay'], is_admin=True)
async def pay_group_admin(message: types.Message):
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
async def pay_not_group_admin(message: types.Message):
    if await throttling_all(message):
        await message.reply("Чтобы управлять счётом, нужно быть администратором группы.")


# Выдача монет от владельца бота
@dp.message_handler(commands=['give'], is_owner=True)
async def give_money(message: types.Message):
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
async def give_money_no_access(message: types.Message):
    if await throttling_all(message):
        await message.reply("Недоступно!")


# Проверка на пидораса
@dp.message_handler(commands=['fagot'], is_group=True)
async def fagot_check(message: types.Message):
    if await throttling_all(message):
        await fagot_(message)


# Проверка на пидораса в привате не работает
@dp.message_handler(commands=['fagot'], is_private=True)
async def fagot_check_private(message: types.Message):
    if await throttling_all(message):
        await message.reply("Только в группе, при всех >:")


# Немного информации о боте
@dp.message_handler(commands=['info'])
async def bot_info(message: types.Message):
    if await throttling_all(message):
        await message.reply(config.BOT_INFO)


# Ну и подсказки по боту
@dp.message_handler(commands=['faq'])
async def bot_faq(message: types.Message):
    if await throttling_all(message):
        await message.reply(config.BOT_FAQ)


# Испытаем удачу
@dp.message_handler(commands=['dice'])
async def dice_(message: types.Message):
    if await throttling_all(message):
        if uniform(0, 1) >= 0.4:
            if uniform(0, 1) > 0.3:
                value_ = randint(1, 10) + (randint(30, 200) / uniform(2, 5))
                database.PostSQL(message).modify_balance(value_, custom_user=message.from_user.id)
                bot_msg = await message.reply("Тебе выпало %d гривен!" % value_)
            else:
                item_ = await item_dice()
                await give_item(message, item_['id'])
                bot_msg = await message.reply("Тебе выпало %s %s (стоимость %d гривен)" % (
                    item_['icon'], item_['name'], item_['price']
                ))
        else:
            bot_msg = await message.reply("Тебе не повезло. Ничего не выпало... :(")
        await cleaner_body(bot_msg)


# Добавим и возможноть посмотреть кто там самый богатый
@dp.message_handler(commands=['top'])
async def top_users(message: types.Message):
    if await throttling_all(message):
        data = database.PostSQL(message).get_top_balance()
        top_ = "\n".join(
            ["<b>%d.</b> <i>%s</i> <b>-</b> <code>%s</code> <b>гривен</b> | <b>«%d»</b>" %
             (i + 1, e[0], human_format(int(e[1])), e[2]) for i, e in enumerate(data)]
        )
        bot_msg = await message.reply("%s\n\n%s\n\n%s" % (
            "<b>- Топ 10 -</b>", top_,
            "<i>Общая сумма у всех пользователей бота</i> <code>%s</code> <b>гривен</b>" %
            human_format(int(database.PostSQL(message).get_sum_balance()))
        ))
        await cleaner_body(bot_msg)


# Слушаем группу, и выдаём для группы вознаграждение за актив
@dp.message_handler(is_group=True)
async def group_echo(message: types.Message):
    await private_balance_create(message, pass_check=True, cust_usr=message.from_user.id)
    await ask_(message)

    if uniform(0, 1) >= 0.95:
        value_ = randint(5, 100)
        value_for_user = randint(1, 50)

        database.PostSQL(message).modify_balance(value_)

        try:
            database.PostSQL(message).modify_balance(
                value_for_user, custom_user=message.from_user.id,
            )
            await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - <b>%d</b> гривен"
                "\nТакже случайному участнику <b>%s</b> - <b>%d</b> гривен" %
                (value_, message.from_user.full_name, value_for_user)
            )
        except Exception as e:
            logging.error(e)
            await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - <b>%d</b> гривен" % value_
            )
