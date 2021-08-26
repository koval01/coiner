import logging
import psycopg2
from aiogram.types.message import Message

from config import DB_HOST, DB_NAME, DB_PASS, DB_USER


class PostSQL:
    def __init__(self, msg: Message, set_private=False) -> None:
        self.conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST
        )
        self.cursor = self.conn.cursor()

        if msg.chat.type in ["group", "supergroup"] and not set_private:
            self.user_id = msg.chat.id
            self.name = msg.chat.title
            self.username = "@group"
        elif msg.chat.type == "private" or set_private:
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

    def add_user(self, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
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

    def get_balance(self, custom_user=0) -> int:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select balance from wallet where user_id = %(user_id)s limit 1',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchall()
        self.finish()
        return result[0][0]

    def get_top_balance(self) -> int:
        self.cursor.execute(
            'select name, balance, user_id from wallet order by balance desc limit 25',
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


class PostSQL_ChatManager:
    def __init__(self, msg: Message) -> None:
        self.conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST
        )
        self.cursor = self.conn.cursor()

        if msg.chat.type in ["group", "supergroup"]:
            self.chat_id = msg.chat.id
            self.name = msg.chat.title
            self.message_id = msg.message_id
        elif msg.chat.type == "private":
            return

    def finish(self) -> None:
        self.cursor.close()
        self.conn.close()

    def get_last_message(self) -> list:
        self.cursor.execute(
            'select chat_id, last_message_id from chat where chat_id = %(chat_id)s limit 1',
            {'chat_id': self.chat_id}
        )
        result = self.cursor.fetchall()
        self.finish()
        return result[0]

    def add_new_chat(self) -> None:
        self.cursor.execute(
            'insert into chat(chat_id, last_message_id) values (%(chat)s, %(last)s);',
            {
                'chat': self.chat_id,
                'last': self.message_id,
            }
        )
        self.conn.commit()
        self.finish()

    def modify_last(self) -> None:
        self.cursor.execute(
            'update chat set last_message_id = %(last)s where chat_id = %(chat)s',
            {
                'chat': self.chat_id,
                'last': self.message_id,
            },
        )
        self.conn.commit()
        self.finish()


