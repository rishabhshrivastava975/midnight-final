from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import ChatPermissions, ChatPrivileges, Message

from permissions import group_admin_only
import storage


def _target_user(message: Message):
    """Get the target user from a reply, or None."""
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None


@group_admin_only
async def ban_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /ban to ban them.")
    await client.ban_chat_member(message.chat.id, target.id)
    await message.reply_text(f"Banned {target.mention}")


@group_admin_only
async def unban_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /unban to unban them.")
    await client.unban_chat_member(message.chat.id, target.id)
    await message.reply_text(f"Unbanned {target.mention}")


@group_admin_only
async def mute_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /mute to mute them.")
    await client.restrict_chat_member(
        message.chat.id, target.id,
        permissions=ChatPermissions(can_send_messages=False),
    )
    await message.reply_text(f"Muted {target.mention}")


@group_admin_only
async def unmute_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /unmute to unmute them.")
    await client.restrict_chat_member(
        message.chat.id, target.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        ),
    )
    await message.reply_text(f"Unmuted {target.mention}")


@group_admin_only
async def promote_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /promote to promote them.")
    await client.promote_chat_member(
        message.chat.id, target.id,
        privileges=ChatPrivileges(
            can_change_info=True, can_delete_messages=True, can_invite_users=True,
            can_restrict_members=True, can_pin_messages=True,
        ),
    )
    await message.reply_text(f"Promoted {target.mention}")


@group_admin_only
async def demote_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /demote to demote them.")
    await client.promote_chat_member(
        message.chat.id, target.id,
        privileges=ChatPrivileges(
            can_change_info=False, can_delete_messages=False, can_invite_users=False,
            can_restrict_members=False, can_pin_messages=False,
        ),
    )
    await message.reply_text(f"Demoted {target.mention}")


@group_admin_only
async def warn_cmd(client: Client, message: Message):
    target = _target_user(message)
    if not target:
        return await message.reply_text("Reply to a user's message with /warn to warn them.")
    count = storage.add_warn(message.chat.id, target.id)
    if count >= 3:
        await client.ban_chat_member(message.chat.id, target.id)
        storage.reset_warns(message.chat.id, target.id)
        await message.reply_text(f"{target.mention} reached 3 warns and was banned.")
    else:
        await message.reply_text(f"Warned {target.mention} ({count}/3)")


@group_admin_only
async def pin_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message with /pin to pin it.")
    await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
    await message.reply_text("Pinned.")


def register(app: Client):
    app.add_handler(MessageHandler(ban_cmd, filters.command("ban") & filters.group))
    app.add_handler(MessageHandler(unban_cmd, filters.command("unban") & filters.group))
    app.add_handler(MessageHandler(mute_cmd, filters.command("mute") & filters.group))
    app.add_handler(MessageHandler(unmute_cmd, filters.command("unmute") & filters.group))
    app.add_handler(MessageHandler(promote_cmd, filters.command("promote") & filters.group))
    app.add_handler(MessageHandler(demote_cmd, filters.command("demote") & filters.group))
    app.add_handler(MessageHandler(warn_cmd, filters.command("warn") & filters.group))
    app.add_handler(MessageHandler(pin_cmd, filters.command("pin") & filters.group))
