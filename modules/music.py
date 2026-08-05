"""
Voice-chat music module.

Uses yt-dlp to resolve a search term/link to a direct audio stream, then
plays it into the group's voice chat via PyTgCalls. Note: streaming audio
pulled from YouTube this way isn't licensed distribution -- fine for a
private/personal group, but worth being aware of if you plan to run this
publicly. See README.md for licensed alternatives (Spotify preview clips,
user-uploaded audio, Creative Commons libraries) if that matters for you.
"""

import asyncio

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp

# chat_id -> [(title, stream_url), ...]
queues: dict[int, list[tuple[str, str]]] = {}


def get_stream_url(query: str) -> tuple[str, str]:
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}" if "http" not in query else query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["title"], info["url"]


def make_handlers(call_py: PyTgCalls):
    async def play_cmd(client: Client, message: Message):
        args = message.command[1:]
        if not args:
            return await message.reply_text("Usage: /play <song name or YouTube link>")

        query = " ".join(args)
        chat_id = message.chat.id
        status = await message.reply_text(f"🔎 Searching for `{query}`...")

        try:
            title, stream_url = await asyncio.to_thread(get_stream_url, query)
        except Exception as e:
            return await status.edit_text(f"Couldn't find that: {e}")

        queues.setdefault(chat_id, [])
        currently_active = chat_id in getattr(call_py, "calls", {})

        if currently_active:
            queues[chat_id].append((title, stream_url))
            return await status.edit_text(f"➕ Queued: **{title}**")

        try:
            await call_py.play(chat_id, MediaStream(stream_url))
            await status.edit_text(f"▶️ Now playing: **{title}**")
        except Exception as e:
            await status.edit_text(f"Failed to join/play: {e}")

    async def skip_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        q = queues.get(chat_id, [])
        if not q:
            await call_py.leave_call(chat_id)
            return await message.reply_text("⏭ Nothing queued next, left the voice chat.")
        title, stream_url = q.pop(0)
        await call_py.play(chat_id, MediaStream(stream_url))
        await message.reply_text(f"⏭ Skipped. Now playing: **{title}**")

    async def stop_cmd(client: Client, message: Message):
        chat_id = message.chat.id
        queues.pop(chat_id, None)
        try:
            await call_py.leave_call(chat_id)
            await message.reply_text("⏹ Stopped and left the voice chat.")
        except Exception:
            await message.reply_text("I'm not in a voice chat here.")

    async def queue_cmd(client: Client, message: Message):
        q = queues.get(message.chat.id, [])
        if not q:
            return await message.reply_text("Queue is empty.")
        lines = [f"{i+1}. {title}" for i, (title, _) in enumerate(q)]
        await message.reply_text("🎶 Queue:\n" + "\n".join(lines))

    return play_cmd, skip_cmd, stop_cmd, queue_cmd


def register(app: Client, call_py: PyTgCalls):
    play_cmd, skip_cmd, stop_cmd, queue_cmd = make_handlers(call_py)
    app.add_handler(MessageHandler(play_cmd, filters.command("play") & filters.group))
    app.add_handler(MessageHandler(skip_cmd, filters.command("skip") & filters.group))
    app.add_handler(MessageHandler(stop_cmd, filters.command("stop") & filters.group))
    app.add_handler(MessageHandler(queue_cmd, filters.command("queue") & filters.group))
