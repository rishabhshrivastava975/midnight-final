from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from permissions import group_admin_only
import storage

AVAILABLE_THEMES = ["default", "dark", "sakura", "neon", "gold"]


@group_admin_only
async def set_theme_cmd(client: Client, message: Message):
    args = message.command[1:]
    if not args or args[0].lower() not in AVAILABLE_THEMES:
        return await message.reply_text(
            f"Usage: /settheme <name>\nAvailable: {', '.join(AVAILABLE_THEMES)}"
        )
    theme = args[0].lower()
    storage.set_theme(message.chat.id, theme)
    await message.reply_text(f"Theme set to '{theme}' for this chat.")


async def theme_cmd(client: Client, message: Message):
    theme = storage.get_theme(message.chat.id)
    await message.reply_text(f"Current theme: {theme}")


def register(app: Client):
    app.add_handler(MessageHandler(set_theme_cmd, filters.command("settheme") & filters.group))
    app.add_handler(MessageHandler(theme_cmd, filters.command("theme")))
