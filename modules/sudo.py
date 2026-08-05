from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from permissions import owner_only
import storage


@owner_only
async def addsudo_cmd(client: Client, message: Message):
    args = message.command[1:]
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    elif args and args[0].isdigit():
        target_id = int(args[0])
    else:
        return await message.reply_text("Reply to a user or use /addsudo <user_id>")
    storage.add_sudo(target_id)
    await message.reply_text(f"Added {target_id} as sudo user.")


@owner_only
async def delsudo_cmd(client: Client, message: Message):
    args = message.command[1:]
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
    elif args and args[0].isdigit():
        target_id = int(args[0])
    else:
        return await message.reply_text("Reply to a user or use /delsudo <user_id>")
    storage.del_sudo(target_id)
    await message.reply_text(f"Removed {target_id} from sudo users.")


async def sudolist_cmd(client: Client, message: Message):
    users = storage.list_sudo()
    if not users:
        return await message.reply_text("No sudo users added yet.")
    await message.reply_text("Sudo users:\n" + "\n".join(str(u) for u in users))


@owner_only
async def broadcast_cmd(client: Client, message: Message):
    # NOTE: this is a stub. Real broadcast needs a table of known chat_ids,
    # which you'd populate as the bot is added to groups.
    args = message.command[1:]
    if not args:
        return await message.reply_text("Usage: /broadcast <message>")
    await message.reply_text(
        "Broadcast stub received: " + " ".join(args) +
        "\n(Wire this to a saved chat_id list to actually send it out.)"
    )


def register(app: Client):
    app.add_handler(MessageHandler(addsudo_cmd, filters.command("addsudo")))
    app.add_handler(MessageHandler(delsudo_cmd, filters.command("delsudo")))
    app.add_handler(MessageHandler(sudolist_cmd, filters.command("sudolist")))
    app.add_handler(MessageHandler(broadcast_cmd, filters.command("broadcast")))
