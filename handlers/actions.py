import logging
from random import uniform, randint

from aiogram import types
from aiogram.types.message import Message
from aiogram.utils.exceptions import Throttled

import config
import database
from additional.buy_slave import init_transaction_ as slave_buy_
from dispatcher import dp
from additional.entertainment import ask_, fagot_
from additional.give import init_give
from additional.inventory import take_item, item_dice, give_item, take_all_items
from additional.items import items_ as all_items
from additional.pay import init_pay
from special.throttling import rate_limit
from special.utils import human_format
from .cleaner import cleaner_body


# Глобальная функция для создания счёта юзера
async def private_balance_create(message: Message, pass_check=False, cust_usr=0) -> None:
    data = database.PostSQL(message, set_private=pass_check).check_user(custom_user=cust_usr)
    if data:
        try:
            if message.from_user.full_name and \
                    message.from_user.full_name != data["name"]:
                database.PostSQL(message).modify_name_(
                    name=message.from_user.full_name)
        except Exception as e:
            logging.debug(e)

        try:
            if message.chat.title and \
                    message.chat.title != data["name"]:
                database.PostSQL(message).modify_name_(
                    name=message.chat.title)
        except Exception as e:
            logging.debug(e)

        if not pass_check:
            await message.reply("Твой баланс: <b>%d</b> гривен" % database.PostSQL(
                message, set_private=pass_check
            ).get_balance(
                custom_user=cust_usr
            ))
    else:
        database.PostSQL(message, set_private=pass_check).add_user(custom_user=cust_usr)
        database.PostSQL(message, set_private=pass_check).modify_balance(config.START_BALANCE, custom_user=cust_usr)
        await message.reply("Привет <b>%s</b>, твой счёт успешно создан. Также тебе было начислено <b>%d</b> гривен!" % (
            message.from_user.first_name, config.START_BALANCE
        ))


# Создание счёта, доступно тоже для всех
@dp.message_handler(commands=['start'], is_private=True)
@rate_limit(3, 'start_private')
async def start_for_private(message: types.Message):
    await private_balance_create(message)


@dp.message_handler(commands=['start'], is_group=True)
@rate_limit(5, 'start_group')
async def start_for_group(message: types.Message):
    if database.PostSQL(message).check_user():
        bot_msg = await message.reply("Баланс этой группы: %d гривен" % database.PostSQL(message).get_balance())
    else:
        database.PostSQL(message).add_user()
        database.PostSQL(message).modify_balance(config.START_BALANCE)
        bot_msg = await message.reply(
            "Счёт группы успешно создан. Также на баланс группы было начислено <b>%d</b> гривен!" %
            config.START_BALANCE
        )
    await cleaner_body(bot_msg, message)


# Проверка баланса, работает без всяких ограничений
@dp.message_handler(commands=['wallet'], is_private=True)
@rate_limit(1, 'wallet_private')
async def wallet_private(message: types.Message):
    data = database.PostSQL(message).check_user()
    bot_msg = await message.reply(
        "Твой баланс: %d гривен\nНомер счёта: «<code>%d</code>»" % (data["balance"], data["user_id"]))
    await cleaner_body(bot_msg, message)


# И команда для групп конечно
@dp.message_handler(commands=['wallet'], is_group=True)
@rate_limit(3, 'wallet_group')
async def wallet_group(message: types.Message):
    data = database.PostSQL(message).check_user()
    bot_msg = await message.reply(
        "Баланс группы: %d гривен\nНомер счёта группы: «<code>%d</code>»" % (data["balance"], data["user_id"]))
    await cleaner_body(bot_msg, message)


# Если вызвали из приватного чата
@dp.message_handler(commands=['pay'], is_private=True)
@rate_limit(3, 'pay_private')
async def pay_in_private(message: types.Message):
    try:
        u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
        if u_ == message.chat.id:
            bot_msg = await message.reply("Какое-то странное действие.")
            return
        x = await init_pay(message, s_, u_)
        if x:
            bot_msg = await message.reply("Получатель: <b>%d</b>\nСумма: <b>%d</b>" % (
                u_, s_
            ))
    except Exception as e:
        logging.debug(e)
        bot_msg = await message.reply("/pay *получатель* *сумма*")
    await cleaner_body(bot_msg, message)


@dp.message_handler(commands=['buyslave'])
@rate_limit(1, 'buy_slave')
async def buy_slave_private(message: types.Message):
    try:
        x = await slave_buy_(message)
        if x:
            bot_msg = await message.reply("Ты успешно купил нового раба >:)")
            await cleaner_body(bot_msg, message)
    except Exception as e:
        logging.debug(e)


@dp.message_handler(commands=['slaves'])
@rate_limit(1, 'slaves_count')
async def user_slaves(message: types.Message):
    data = int(database.PostSQL(message).get_slaves(
        custom_user=message.from_user.id))
    bot_msg = await message.reply("У тебя <b>%d</b> рабов\nДоход с них <b>%d</b> гривен в час" % (
        data, data * config.PAY_PER_SLAVE
    ))
    await cleaner_body(bot_msg, message)


# Можно даже глянуть свой инвентарь
@dp.message_handler(commands=['inventory'])
@rate_limit(5, 'inventory_view')
async def user_inventory(message: types.Message):
    try:
        try:
            inv_user_id = int(message.text.split()[1])
        except:
            inv_user_id = message.from_user.id
        additional_text_inv = None
        if inv_user_id <= 0:
            bot_msg = await message.reply("Возможно неверный идентификатор.")
            return
        if inv_user_id:
            data_user = database.PostSQL().check_user(inv_user_id)
            additional_text_inv = "Вещи <b>%s</b>" % data_user["name"]
        data = database.PostSQL_Inventory(message).get_inventory(inv_user_id)
        items_price = sum([all_items[el["item_id"]]["price"] for el in data])
        price_text = "Общая цена <code>%s</code> гривен" % human_format(items_price)
        items_ = "\n".join(
            ["(<b>%d</b>) %s <b>%s</b> (<b>%d</b> гривен)" %
             (
                 i["id"],
                 all_items[i["item_id"]]["icon"],
                 all_items[i["item_id"]]["name"],
                 all_items[i["item_id"]]["price"]
             ) for i in data]
        )
        bot_msg = await message.reply("%s\n\n%s\n%s\n%s\nСлотов занято: <b>%d/50</b>" % (
            items_, "_" * 10, additional_text_inv, price_text, len(data)))
    except Exception as e:
        logging.debug("Error in inventory function: %s" % e)
        bot_msg = await message.reply("Что-то пошло не так...")
    await cleaner_body(bot_msg, message)


@dp.message_handler(commands=['search'])
@rate_limit(2, 'search_user')
async def search_user(message: types.Message):
    try:
        text = message.text.split()[1]
        comment = ""
        if len(text) >= 3 and len(text) <= 25:
            data = database.PostSQL().search_user(text)
            top_ = ["<i>%s</i> <b>-</b> <code>%s</code> <b>гривен</b> | <b>«<code>%d</code>»</b>" %
                    (i["name"], human_format(int(i["balance"])), i["user_id"]) for i in data]
            if len(top_) == 0:
                bot_msg = await message.reply("Ничего не найдено.")
                return
            if len(top_) > 50:
                comment = "%s\nПоказано 50 из %d. Попробуй уточнить запрос." % ('_' * 10, len(top_))
            result = "\n".join(top_)
            bot_msg = await message.reply("По запросу <code>%s</code> найдено:\n%s\n%s" % (
                text, result, comment))
        else:
            bot_msg = await message.reply("Минимальная длина 3 символа, а максимальная 25.")
    except Exception as e:
        logging.error("Error search user. Details: %s" % e)
        bot_msg = await message.reply("Пример - /search elo")
    await cleaner_body(bot_msg, message)


# Продажа предметов
@dp.message_handler(commands=['sell'])
@rate_limit(2, 'sell_item')
async def sell__(message: types.Message):
    try:
        item_id = int(message.text.split()[1])
        data_ = database.PostSQL_Inventory(message).get_item(item_id)
        if int(data_["owner_id"]) != message.from_user.id:
            bot_msg = await message.reply("Мне кажется или этот предмет не твой"
                                          "\nТы меня обмануть решил что ли? Гадёныш, "
                                          "иди делом лучше займись!")
            return

        x = await take_item(message, item_id)
        item__ = all_items[int(data_["item_id"])]
        item_price = item__["price"]
        if x:
            await init_give(message, item_price, item_sell=True)
            bot_msg = await message.reply("Предмет %s <b>%s</b> был продан за <b>%d</b> гривен!" % (
                item__["icon"], item__["name"], item_price
            ))
    except Exception as e:
        logging.info(e)
        bot_msg = await message.reply(
            "/sell *ID предмета*"
            "\n\nПример: (*ID предмета*) 🇺🇸 "
            "Флаг США (15000 гривен)"
        )
    await cleaner_body(bot_msg, message)


# Продажа всего инвентаря сразу
@dp.message_handler(commands=['sellall'])
@rate_limit(5, 'sell_all_items')
async def sell_all_items(message: types.Message):
    try:
        items_price = sum(
            [all_items[el["item_id"]]["price"] for el in database.PostSQL_Inventory(message).get_inventory()])
        x = await take_all_items(message)
        if x:
            await init_give(message, items_price, item_sell=True)
            bot_msg = await message.reply("Предметы были проданы за <b>%s</b> гривен!" % human_format(items_price))
        else:
            bot_msg = await message.reply("Не удалось продать предметы.")
    except Exception as e:
        logging.info(e)
        bot_msg = await message.reply("Произошла ошибка, похоже что у тебя нет предметов.")
    await cleaner_body(bot_msg, message)


# Если вызвал админ из группы
@dp.message_handler(commands=['pay'], is_admin=True)
@rate_limit(10, 'privileged_pay_group')
async def pay_group_admin(message: types.Message):
    try:
        u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
        if u_ == message.chat.id:
            bot_msg = await message.reply("Какое-то странное действие.")
            return
        x = await init_pay(message, s_, u_)
        if x:
            bot_msg = await message.reply("Получатель: <b>%d</b>\nСумма: <b>%d</b>" % (
                u_, s_
            ))
        else:
            bot_msg = await message.reply("Не удалось продать предметы.")
    except Exception as e:
        logging.debug(e)
        bot_msg = await message.reply("/pay *получатель* *сумма*")
    await cleaner_body(bot_msg, message)


@dp.message_handler(commands=['dice_switch'], is_admin=True)
@rate_limit(10, 'privileged_dice_switch_group')
async def dice_switch_group_admin(message: types.Message):
    if database.PostSQL(message).get_dice_on(custom_user=message.chat.id):
        database.PostSQL(message).update_dice_on(message.chat.id, status=False)
        bot_msg = await message.reply("Теперь в этой группе <b>нельзя</b> использовать dice")
    else:
        database.PostSQL(message).update_dice_on(message.chat.id, status=True)
        bot_msg = await message.reply("Теперь в этой группе <b>можно</b> использовать dice")
    await cleaner_body(bot_msg, message)


# Если вызвал участник группы, без прав администратора
@dp.message_handler(commands=['pay'], is_admin=False)
@rate_limit(30, 'not_privileged_pay_group')
async def pay_not_group_admin(message: types.Message):
    bot_msg = await message.reply("Чтобы управлять счётом, нужно быть администратором группы.")
    await cleaner_body(bot_msg, message)


@dp.message_handler(commands=['dice_switch'], is_admin=False)
@rate_limit(30, 'not_privileged_dice_switch_group')
async def dice_switch_not_group_admin(message: types.Message):
    bot_msg = await message.reply("Чтобы управлять фильтром dice, нужно быть администратором группы.")
    await cleaner_body(bot_msg, message)


# Выдача монет от владельца бота
@dp.message_handler(commands=['give'], is_owner=True)
@rate_limit(3, 'give_coins')
async def give_money(message: types.Message):
    try:
        u_, s_ = int(message.text.split()[1]), int(message.text.split()[2])
        data = database.PostSQL(message).check_user(custom_user=u_)
        x = await init_give(message, s_, u_, "Администрация")
        if x:
            bot_msg = await message.reply("Для <b>%s</b> было выдано <b>%d</b> гривен!" % (
                data["name"], s_
            ))
    except Exception as e:
        logging.debug(e)
        bot_msg = await message.reply("/give *получатель* *сумма*")
    await cleaner_body(bot_msg, message)


# Если у пользователя нет прав на эту команду
@dp.message_handler(commands=['give'], is_owner=False)
@rate_limit(10, 'give_coins_forbidden')
async def give_money_no_access(message: types.Message):
    bot_msg = await message.reply("Недоступно!")
    await cleaner_body(bot_msg, message)


# Проверка на пидораса
@dp.message_handler(commands=['fagot'], is_group=True)
@rate_limit(600, 'fagot_test')
async def fagot_check(message: types.Message):
    await fagot_(message)


# Проверка на пидораса в привате не работает
@dp.message_handler(commands=['fagot'], is_private=True)
@rate_limit(1, 'fagot_test_private')
async def fagot_check_private(message: types.Message):
    await message.reply("Только в группе, при всех >:")


# Немного информации о боте
@dp.message_handler(commands=['info'])
@rate_limit(30, 'info')
async def bot_info(message: types.Message):
    bot_msg = await message.reply(config.BOT_INFO)
    await cleaner_body(bot_msg, message)


# Ну и подсказки по боту
@dp.message_handler(commands=['faq'])
@rate_limit(30, 'faq')
async def bot_faq(message: types.Message):
    bot_msg = await message.reply(config.BOT_FAQ)
    await cleaner_body(bot_msg, message)


# Испытаем удачу
@dp.message_handler(commands=['dice'])
@rate_limit(0.3, 'dice')
async def dice_(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if not database.PostSQL(message).get_dice_on(custom_user=message.chat.id):
            try:
                await dp.throttle('dice_disabled', rate=10)
            except Throttled:
                pass
            else:
                bot_msg = await message.reply("Администрация этой группы отключила команду dice")
            return
    if uniform(0, 1) >= 0.4:
        if uniform(0, 1) > 0.3:
            value_ = randint(1, 10) + (randint(30, 200) / uniform(2, 5))
            database.PostSQL(message).modify_balance(value_, custom_user=message.from_user.id)
            bot_msg = await message.reply("Тебе выпало <b>%d</b> гривен!" % value_)
        else:
            item_ = await item_dice()
            await give_item(message, item_['id'])
            bot_msg = await message.reply("Тебе выпало %s <b>%s</b> (стоимость <b>%d</b> гривен)" % (
                item_['icon'], item_['name'], item_['price']
            ))
    else:
        bot_msg = await message.reply("Тебе не повезло. Ничего не выпало... :(")
    await cleaner_body(bot_msg, message)


# Добавим и возможноть посмотреть кто там самый богатый
@dp.message_handler(commands=['top'])
@rate_limit(3, 'get_top_list')
async def top_users(message: types.Message):
    data = database.PostSQL(message).get_top_balance
    top_ = "\n".join(
        ["<b>%d.</b> <i>%s</i> <b>-</b> <code>%s</code> <b>гривен</b> | <b>«<code>%d</code>»</b>" %
         (i + 1, e["name"], human_format(int(e["balance"])), e["user_id"]) for i, e in enumerate(data)]
    )
    bot_msg = await message.reply("%s\n\n%s\n\n%s" % (
        "<b>- Топ 10 -</b>", top_,
        "<i>Общая сумма у всех пользователей бота</i> <code>%s</code> <b>гривен</b>" %
        human_format(int(database.PostSQL(message).get_sum_balance))
    ))
    await cleaner_body(bot_msg, message)


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
            bot_msg = await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - <b>%d</b> гривен"
                "\nТакже случайному участнику <b>%s</b> - <b>%d</b> гривен" %
                (value_, message.from_user.full_name, value_for_user)
            )
        except Exception as e:
            logging.error(e)
            bot_msg = await message.answer(
                "За активность в этой группе на баланс группы было зачисленно - <b>%d</b> гривен" % value_
            )
        await cleaner_body(bot_msg)
