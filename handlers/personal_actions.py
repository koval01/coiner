from aiogram import types
from dispatcher import dp
import config


@dp.message_handler(commands=['balance'])
async def check_balance(message: types.Message):
    await message.reply("Твой баланс: %f COINS" % 0.657498786738752)