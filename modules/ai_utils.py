import httpx
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

import config


async def ask_cmd(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        return await message.reply_text("Usage: /ask <question>")
    if not config.ANTHROPIC_API_KEY:
        return await message.reply_text("AI feature not configured. Set ANTHROPIC_API_KEY in .env")
    question = " ".join(args)
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    try:
        async with httpx.AsyncClient(timeout=30) as http_client:
            resp = await http_client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": config.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": question}],
                },
            )
            data = resp.json()
            text = "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            )
            await message.reply_text(text or "No response from AI.")
    except Exception as e:
        await message.reply_text(f"AI request failed: {e}")


async def calc_cmd(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        return await message.reply_text("Usage: /calc <expression>  e.g. /calc 2*(3+4)")
    expr = " ".join(args)
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return await message.reply_text("Only numbers and + - * / ( ) are allowed.")
    try:
        result = eval(expr, {"__builtins__": {}})
        await message.reply_text(f"= {result}")
    except Exception:
        await message.reply_text("Invalid expression.")


async def id_cmd(client: Client, message: Message):
    user = message.from_user
    chat = message.chat
    target = message.reply_to_message.from_user if message.reply_to_message else user
    await message.reply_text(f"👤 User ID: {target.id}\n💬 Chat ID: {chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(ask_cmd, filters.command("ask")))
    app.add_handler(MessageHandler(calc_cmd, filters.command("calc")))
    app.add_handler(MessageHandler(id_cmd, filters.command("id")))
