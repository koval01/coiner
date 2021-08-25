from config import DB_HOST, DB_NAME, DB_PASS, DB_USER
from aiogram.types.message import Message
import psycopg2, logging


class PostSQL:
    def __init__(self, msg: Message) -> None:
        self.conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST
        )
        self.cursor = self.conn.cursor()

        if msg.chat.type in ["group", "supergroup"]:
            self.user_id = msg.chat.id
            self.name = msg.chat.title
            self.username = "@group"
        elif msg.chat.type == "private":
            self.user_id = msg.from_user.id
            self.name = msg.from_user.first_name
            self.username = msg.from_user.username

    def finish(self) -> None:
        self.cursor.close()
        self.conn.close()

    def check_user(self, custom_user=0) -> list:
        if custom_user: self.user_id = custom_user
        try:
            self.cursor.execute(
                'select * from wallet where user_id = %(user_id)s',
                {'user_id': self.user_id},
            )
            result = self.cursor.fetchall()
            self.finish()
            return result[0]
        except Exception as e:
            logging.debug(e)

    def add_user(self) -> None:
        self.cursor.execute(
            'insert into wallet(name, balance, user_id, username) values (%(name)s, 0, %(user_id)s, %(username)s);',
            {
                'user_id': self.user_id,
                'name': self.name,
                'username': self.username,
            }
        )
        self.conn.commit()
        self.finish()

    def get_balance(self) -> int:
        self.cursor.execute(
            'select balance from wallet where user_id = %(user_id)s limit 1',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchall()
        self.finish()
        return result[0][0]

    def get_top_balance(self) -> int:
        self.cursor.execute(
            'select name, balance from wallet order by balance desc limit 20',
        )
        result = self.cursor.fetchall()
        self.finish()
        return result

    def modify_balance(self, coins, take=False, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
        if take: x = "-"
        else: x = "+"
        self.cursor.execute(
            f'update wallet set balance = balance {x} %(coins)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'coins': coins},
        )
        self.conn.commit()
        self.finish()