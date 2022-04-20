import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter, \
    IsPrivateFilter, IsGroupFilter, IsBotAdminFilter

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.BOT_TOKEN:
    exit("No token provided")

# init
storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)
dp.filters_factory.bind(IsPrivateFilter)
dp.filters_factory.bind(IsGroupFilter)
dp.filters_factory.bind(IsBotAdminFilter)
