from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

import config


class IsOwnerFilter(BoundFilter):
    """
    Custom filter "is_owner".
    """
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def check(self, message: types.Message):
        return int(message.from_user.id) == int(config.BOT_OWNER)


class IsBotAdminFilter(BoundFilter):
    """
    Custom filter "is_bot_admin".
    """
    key = "is_bot_admin"

    def __init__(self, is_bot_admin):
        self.is_bot_admin = is_bot_admin

    async def check(self, message: types.Message):
        return (int(message.from_user.id) == int(config.BOT_OWNER)) or \
               (int(message.from_user.id) in config.BOT_ADMINS)


class IsAdminFilter(BoundFilter):
    """
    Filter that checks for admin rights existence
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin


class IsPrivateFilter(BoundFilter):
    """
    Filter for private chat
    """
    key = "is_private"

    def __init__(self, is_private: bool):
        self.is_private = is_private

    async def check(self, message: types.Message):
        return message.chat.type == "private"


class IsGroupFilter(BoundFilter):
    """
    Filter for group chat
    """
    key = "is_group"

    def __init__(self, is_group: bool):
        self.is_group = is_group

    async def check(self, message: types.Message):
        return message.chat.type in ["group", "supergroup"]


class MemberCanRestrictFilter(BoundFilter):
    """
    Filter that checks member ability for restricting
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict
