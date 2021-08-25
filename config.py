import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
BOT_OWNER = os.environ.get("BOT_OWNER", None)

DB_HOST = os.environ.get("DB_HOST", None)
DB_NAME = os.environ.get("DB_NAME", None)
DB_USER = os.environ.get("DB_USER", None)
DB_PASS = os.environ.get("DB_PASS", None)

START_BALANCE = 100

BOT_INFO = """
Этот бот был написан за один день, и не очень сложным. Цель этого бота - развлекать участников групп. 
Участники могут собирать монеты, обмениваться ими, или же собирать их в кошельке группы.

Разработчик: @koval_yaroslav
Код этого бота: github.com/koval01/coiner
"""

BOT_FAQ = """
<i>Могу ли я купить монеты?</i>
<b>- Нет, разве что у другого пользователя.</b>

<i>Как работает троттлинг?</i>
<b>- Задержка считается от момент запроса, а не последнего удачного вызова.</b>

<i>Нужны ли права администратора боту в группе?</i>
<b>- Нет, не нужны.</b>

<i>Можно ли этого бота использовать в приватной группе?</i>
<b>- Да, бота можно использовать в любой группе.</b>
"""