import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_OWNER = os.getenv("BOT_OWNER")
BOT_ADMINS = [int(i) for i in os.getenv("BOT_ADMINS").split()]

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

DATABASE_URL = os.getenv("DATABASE_URL")

GA_ID = os.getenv("GA_ID")
GA_SECRET = os.getenv("GA_SECRET")

START_BALANCE = 5000
START_XP = 0
STATIC_PRICE_DICE = 1000
SLAVE_PRICE_PRC = 32
SLAVE_PRICE = 3100
SLAVES_PAY_NOTIFY = False
PAY_PER_SLAVE = 290
COM_TRANS = 6
CLEANER = True

BOT_INFO = """
Этот бот был написан за один день, и не очень сложным. Цель этого бота - развлекать участников групп. 
Участники могут собирать гривны, обмениваться ими, или же собирать их в кошельке группы.

Разработчик: @KovalYRS
"""

BOT_FAQ = """
<i>Могу ли я купить гривны?</i>
<b>- Нет, разве что у другого пользователя.</b>

<i>Как работает троттлинг?</i>
<b>- Задержка считается от момент запроса, а не последнего удачного вызова.</b>

<i>Нужны ли права администратора боту в группе?</i>
<b>- Нет, не нужны.</b>

<i>Можно ли этого бота использовать в приватной группе?</i>
<b>- Да, бота можно использовать в любой группе.</b>
"""
