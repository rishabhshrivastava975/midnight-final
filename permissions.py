from functools import wraps

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import Message

import config
import storage


def is_owner(user_id: int) -> bool:
    return user_id == config.OWNER_ID


def is_sudo(user_id: int) -> bool:
    return is_owner(user_id) or user_id in config.SUDO_USERS or user_id in storage.list_sudo()


def owner_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *a, **kw):
        if not message.from_user or not is_owner(message.from_user.id):
            await message.reply_text("This command is owner-only.")
            return
        return await func(client, message, *a, **kw)
    return wrapper


def sudo_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *a, **kw):
        if not message.from_user or not is_sudo(message.from_user.id):
            await message.reply_text("This command is sudo-only.")
            return
        return await func(client, message, *a, **kw)
    return wrapper


async def user_is_chat_admin(client: Client, message: Message) -> bool:
    if message.chat.type == ChatType.PRIVATE:
        return True
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


def group_admin_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *a, **kw):
        if not await user_is_chat_admin(client, message):
            await message.reply_text("You need to be a group admin to use this.")
            return
        return await func(client, message, *a, **kw)
    return wrapper
