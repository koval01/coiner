import logging
import re

import psycopg2
import psycopg2.extras
from aiogram.types.message import Message
from special.utils import cleaner_name

from config import DATABASE_URL


class PostgreSQL_Paser(object):
    def __init__(self) -> None:
        self.pattern = re.compile(
            r"postgres://(?P<user>[0-9A-Za-z]*):(?P<password>[0-9A-Za-z]*)"
            r"@(?P<host>[0-9A-Za-z-.]*):(?P<port>[0-9]{4})/(?P<dbname>[0-9A-Za-z]*)"
        )

    @property
    def get(self) -> dict:
        return re.search(self.pattern, DATABASE_URL).groupdict()


class PostSQL:
    def __init__(self, msg: Message = None, set_private=False) -> None:
        self.conn = psycopg2.connect(**PostgreSQL_Paser().get)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.taker = lambda x: "-" if x else "+"

        try:
            #  Проверяем есть ли message
            if msg: pass
        except Exception as e:
            logging.debug(e)

        try:
            #  Если нету msg, то просто скипаем этот блок
            self.message_id = msg.message_id
            if msg.chat.type in ["group", "supergroup"] and not set_private:
                self.user_id = msg.chat.id
                self.name = msg.chat.title
                self.username = "@group"
            elif msg.chat.type == "private" or set_private:
                self.user_id = msg.from_user.id
                self.name = cleaner_name(msg.from_user.first_name)
                self.username = msg.from_user.username
        except Exception as e:
            logging.debug(e)

    @property
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
            result = self.cursor.fetchone()
            self.finish
            return result
        except Exception as e:
            logging.debug(e)

    @property
    def modify_last_msg_slaves(self) -> None:
        self.cursor.execute(
            'update wallet set slaves_last_msg = %(last)s where user_id = %(chat)s',
            {
                'chat': self.user_id,
                'last': self.message_id
            },
        )
        self.conn.commit()
        self.finish

    def search_user(self, search_text: str) -> list:
        try:
            self.cursor.execute(
                'select * from wallet where lower(name) like lower(%(search_text)s)',
                {'search_text': f'%{search_text}%'},
            )
            result = self.cursor.fetchall()
            self.finish
            return result
        except Exception as e:
            logging.debug(e)

    def add_user(self, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'insert into wallet(name, balance, user_id, username, slaves) '
            'values (%(name)s, 0, %(user_id)s, %(username)s, 0)',
            {
                'user_id': self.user_id,
                'name': self.name,
                'username': self.username,
            }
        )
        self.conn.commit()
        self.finish

    def get_balance(self, custom_user=0) -> int:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select balance from wallet where user_id = %(user_id)s',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchone()
        self.finish
        return result["balance"]

    @property
    def get_inv_sort_mode(self) -> int:
        self.cursor.execute(
            'select inv_sort_mode from wallet where user_id = %(user_id)s',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchone()
        self.finish
        return result["inv_sort_mode"]

    def set_inv_sort_mode(self, state: int = 0) -> None:
        self.cursor.execute(
            'update wallet set inv_sort_mode = %(state)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'state': state},
        )
        self.conn.commit()
        self.finish

    @property
    def get_last_slaves_message(self) -> int:
        self.cursor.execute(
            'select slaves_last_msg from wallet where user_id = %(user_id)s',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchone()
        self.finish
        return result["slaves_last_msg"]

    def get_dice_on(self, custom_user=0) -> float:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select dice_on from wallet where user_id = %(user_id)s',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchone()
        self.finish
        return result["dice_on"]

    def update_dice_on(self, custom_user=0, status: bool = True) -> None:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'update wallet set dice_on = %(status)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'status': status},
        )
        self.conn.commit()
        self.finish

    @property
    def get_sum_balance(self) -> int:
        self.cursor.execute(
            'select sum(balance) from wallet',
        )
        result = self.cursor.fetchone()
        self.finish
        return result["sum"]

    @property
    def get_top_balance(self) -> list:
        self.cursor.execute(
            'select name, balance, user_id from wallet order by balance desc limit 10',
        )
        result = self.cursor.fetchall()
        self.finish
        return result

    @property
    def get_users_ids_list(self) -> list:
        self.cursor.execute('select user_id from wallet')
        result = self.cursor.fetchall()
        self.finish
        return result

    def modify_name_(self, name, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'update wallet set name = %(name)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'name': name},
        )
        self.conn.commit()
        self.finish

    def modify_balance(self, coins, take=False, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            f'update wallet set balance = balance {self.taker(take)} %(coins)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'coins': coins},
        )
        self.conn.commit()
        self.finish

    def modify_slaves(self, slaves=1, take=False, custom_user=0) -> None:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            f'update wallet set slaves = slaves {self.taker(take)} %(slaves)s where user_id = %(user_id)s',
            {'user_id': self.user_id, 'slaves': slaves},
        )
        self.conn.commit()
        self.finish

    def get_slaves(self, custom_user=0) -> int:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select slaves from wallet where user_id = %(user_id)s limit 1',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchone()
        self.finish
        return result["slaves"]

    @property
    def get_slave_owners(self) -> int:
        self.cursor.execute(
            'select user_id, slaves from wallet where slaves > 0',
        )
        result = self.cursor.fetchall()
        self.finish
        return result


class PostSQL_ChatManager:
    def __init__(self, msg: Message, msg_user: Message = None) -> None:
        self.conn = psycopg2.connect(**PostgreSQL_Paser().get)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if msg.chat.type in ["group", "supergroup"]:
            self.chat_id = msg.chat.id
            self.name = cleaner_name(msg.chat.title)
            self.message_id = msg.message_id
        elif msg.chat.type == "private":
            return

        if msg_user:
            self.message_id_from_user = msg_user.message_id
        else:
            self.message_id_from_user = 0

    @property
    def finish(self) -> None:
        self.cursor.close()
        self.conn.close()

    @property
    def get_last_message(self) -> list:
        self.cursor.execute(
            'select chat_id, last_message_id, last_user_message_id from chat where chat_id = %(chat_id)s limit 1',
            {'chat_id': self.chat_id}
        )
        result = self.cursor.fetchall()
        self.finish
        return result[0]

    @property
    def add_new_chat(self) -> None:
        self.cursor.execute(
            'insert into chat(chat_id, last_message_id, last_user_message_id) '
            'values (%(chat)s, %(last)s, %(user_last)s)',
            {
                'chat': self.chat_id,
                'last': self.message_id,
                'user_last': self.message_id_from_user
            }
        )
        self.conn.commit()
        self.finish

    @property
    def modify_last(self) -> None:
        self.cursor.execute(
            'update chat set last_message_id = %(last)s, last_user_message_id = %(last_usr)s where chat_id = %(chat)s',
            {
                'chat': self.chat_id,
                'last': self.message_id,
                'last_usr': self.message_id_from_user
            },
        )
        self.conn.commit()
        self.finish


class PostSQL_Inventory:
    def __init__(self, msg: Message) -> None:
        self.conn = psycopg2.connect(**PostgreSQL_Paser().get)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        self.user_id = msg.from_user.id
        self.name = cleaner_name(msg.from_user.first_name)
        self.username = msg.from_user.username

        # Inventory for only private chats IDs

    @property
    def finish(self) -> None:
        self.cursor.close()
        self.conn.close()

    def get_inventory(self, custom_user=0) -> int:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select item_id, id from inventory where owner_id = %(user_id)s order by id desc',
            {'user_id': self.user_id},
        )
        result = self.cursor.fetchall()
        self.finish
        return result

    def get_item(self, item_id_row, custom_user=0) -> int:
        if custom_user: self.user_id = custom_user
        self.cursor.execute(
            'select item_id, id, owner_id from inventory where id = %(item_id)s',
            {'item_id': item_id_row},
        )
        result = self.cursor.fetchall()
        self.finish
        return result[0]

    def give_item(self, item_id) -> None:
        self.cursor.execute(
            'insert into inventory(owner_id, item_id) values (%(chat)s, %(item)s)',
            {
                'chat': self.user_id,
                'item': item_id,
            }
        )
        self.conn.commit()
        self.finish

    def take_item(self, item_id_row) -> None:
        self.cursor.execute(
            'delete from inventory where id = %(item_id)s',
            {
                'item_id': item_id_row,
            }
        )
        self.conn.commit()
        self.finish

    def clear_inventory(self, owner_items: int = 0) -> None:
        if not owner_items:
            owner_items = self.user_id
        self.cursor.execute(
            'delete from inventory where owner_id = %(owner_id)s',
            {
                'owner_id': owner_items,
            }
        )
        self.conn.commit()
        self.finish
