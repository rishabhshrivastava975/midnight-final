import httpx
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

# nekos.best is a free public API for anime reaction gifs, no key needed
NEKOS_BASE = "https://nekos.best/api/v2"

ACTIONS = ["hug", "pat", "slap", "poke", "cuddle", "kiss", "wave", "highfive"]


async def _send_action(message: Message, action: str):
    target = message.reply_to_message.from_user if message.reply_to_message else None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{NEKOS_BASE}/{action}")
            data = resp.json()
            url = data["results"][0]["url"]
    except Exception:
        return await message.reply_text("Couldn't fetch a gif right now, try again.")
    who = (
        f"{message.from_user.first_name} {action}s {target.first_name}!"
        if target
        else f"{message.from_user.first_name} {action}s the air!"
    )
    await message.reply_animation(animation=url, caption=who)


def make_handler(action):
    async def handler(client: Client, message: Message):
        await _send_action(message, action)
    return handler


def register(app: Client):
    for action in ACTIONS:
        app.add_handler(MessageHandler(make_handler(action), filters.command(action)))
