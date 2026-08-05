import random
import time

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

import storage

DAILY_AMOUNT = 500
DAILY_COOLDOWN = 24 * 3600
WORK_MIN, WORK_MAX = 50, 300
WORK_COOLDOWN = 3600


async def balance_cmd(client: Client, message: Message):
    user = message.from_user
    bal, bank = storage.get_balance(user.id)
    await message.reply_text(f"💰 Wallet: {bal}\n🏦 Bank: {bank}\n📊 Total: {bal + bank}")


async def daily_cmd(client: Client, message: Message):
    user = message.from_user
    now = int(time.time())
    last = storage.get_last(user.id, "last_daily")
    if now - last < DAILY_COOLDOWN:
        remaining = DAILY_COOLDOWN - (now - last)
        h, m = divmod(remaining // 60, 60)
        return await message.reply_text(f"Already claimed. Try again in {h}h {m}m.")
    storage.change_balance(user.id, DAILY_AMOUNT)
    storage.set_last(user.id, "last_daily", now)
    await message.reply_text(f"You claimed your daily reward of {DAILY_AMOUNT} coins!")


async def work_cmd(client: Client, message: Message):
    user = message.from_user
    now = int(time.time())
    last = storage.get_last(user.id, "last_work")
    if now - last < WORK_COOLDOWN:
        remaining = WORK_COOLDOWN - (now - last)
        m = remaining // 60
        return await message.reply_text(f"You're tired. Rest for {m}m before working again.")
    earned = random.randint(WORK_MIN, WORK_MAX)
    storage.change_balance(user.id, earned)
    storage.set_last(user.id, "last_work", now)
    await message.reply_text(f"You worked and earned {earned} coins!")


async def deposit_cmd(client: Client, message: Message):
    user = message.from_user
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply_text("Usage: /deposit <amount>")
    amount = int(args[0])
    bal, _ = storage.get_balance(user.id)
    if amount <= 0 or amount > bal:
        return await message.reply_text("Invalid amount.")
    storage.change_balance(user.id, -amount)
    storage.change_bank(user.id, amount)
    await message.reply_text(f"Deposited {amount} coins to your bank.")


async def withdraw_cmd(client: Client, message: Message):
    user = message.from_user
    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply_text("Usage: /withdraw <amount>")
    amount = int(args[0])
    _, bank = storage.get_balance(user.id)
    if amount <= 0 or amount > bank:
        return await message.reply_text("Invalid amount.")
    storage.change_bank(user.id, -amount)
    storage.change_balance(user.id, amount)
    await message.reply_text(f"Withdrew {amount} coins from your bank.")


async def pay_cmd(client: Client, message: Message):
    user = message.from_user
    args = message.command[1:]
    if not message.reply_to_message or not args or not args[0].isdigit():
        return await message.reply_text("Reply to a user with /pay <amount>")
    target = message.reply_to_message.from_user
    amount = int(args[0])
    if target.id == user.id:
        return await message.reply_text("You can't pay yourself.")
    ok = storage.transfer(user.id, target.id, amount)
    if ok:
        await message.reply_text(f"Sent {amount} coins to {target.mention}")
    else:
        await message.reply_text("Insufficient balance.")


async def leaderboard_cmd(client: Client, message: Message):
    rows = storage.leaderboard(10)
    if not rows:
        return await message.reply_text("No data yet.")
    lines = ["🏆 Leaderboard:"]
    for i, (user_id, total) in enumerate(rows, start=1):
        lines.append(f"{i}. {user_id} — {total} coins")
    await message.reply_text("\n".join(lines))


def register(app: Client):
    app.add_handler(MessageHandler(balance_cmd, filters.command("balance")))
    app.add_handler(MessageHandler(daily_cmd, filters.command("daily")))
    app.add_handler(MessageHandler(work_cmd, filters.command("work")))
    app.add_handler(MessageHandler(deposit_cmd, filters.command("deposit")))
    app.add_handler(MessageHandler(withdraw_cmd, filters.command("withdraw")))
    app.add_handler(MessageHandler(pay_cmd, filters.command("pay")))
    app.add_handler(MessageHandler(leaderboard_cmd, filters.command("leaderboard")))
