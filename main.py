import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pytgcalls import PyTgCalls

import config
import storage
from modules import admin, economy, casino, ai_utils, anime, theme, sudo, music

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Clients ---
bot = Client("midnight_bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("midnight_assistant", api_id=config.API_ID, api_hash=config.API_HASH,
                    session_string=config.STRING_SESSION)
call_py = PyTgCalls(assistant)


async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        f"🌙 Hi! I'm **{config.BOT_NAME}**, your all-in-one group bot.\n\n"
        "Use /help to see everything I can do."
    )


async def help_cmd(client: Client, message: Message):
    text = (
        "📖 Commands\n\n"
        "🎵 Music/VC: /play /skip /stop /queue\n"
        "🛡 Admin: /ban /unban /mute /unmute /promote /demote /warn /pin\n"
        "💰 Economy: /balance /daily /work /deposit /withdraw /pay /leaderboard\n"
        "🎰 Casino: /coinflip /dice /slots\n"
        "🤖 AI/Utils: /ask /calc /id\n"
        "🎌 Anime: /hug /pat /slap /poke /cuddle /kiss /wave /highfive\n"
        "🎨 Theme: /theme /settheme\n"
        "👑 Sudo: /addsudo /delsudo /sudolist /broadcast"
    )
    await message.reply_text(text)


def register_all():
    bot.add_handler(MessageHandler(start_cmd, filters.command("start")))
    bot.add_handler(MessageHandler(help_cmd, filters.command("help")))

    admin.register(bot)
    economy.register(bot)
    casino.register(bot)
    ai_utils.register(bot)
    anime.register(bot)
    theme.register(bot)
    sudo.register(bot)
    music.register(bot, call_py)


async def main():
    storage.init_db()
    register_all()

    await assistant.start()
    await bot.start()
    await call_py.start()

    logger.info(f"{config.BOT_NAME} is up and running.")
    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
