import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
BOT_OWNER = os.environ.get("BOT_OWNER", None)

DB_HOST = os.environ.get("DB_HOST", None)
DB_NAME = os.environ.get("DB_NAME", None)
DB_USER = os.environ.get("DB_USER", None)
DB_PASS = os.environ.get("DB_PASS", None)

START_BALANCE = 5000
START_XP = 0
STATIC_PRICE_DICE = 1000
SLAVE_PRICE_PRC = 32
SLAVE_PRICE = 3100
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
