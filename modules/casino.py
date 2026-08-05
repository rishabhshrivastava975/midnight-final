import random

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

import storage


def _parse_bet(args, bal):
    if not args:
        return None
    arg = args[0]
    if arg.lower() == "all":
        return bal
    if arg.isdigit():
        return int(arg)
    return None


async def coinflip_cmd(client: Client, message: Message):
    user = message.from_user
    bal, _ = storage.get_balance(user.id)
    bet = _parse_bet(message.command[1:], bal)
    if bet is None or bet <= 0 or bet > bal:
        return await message.reply_text("Usage: /coinflip <amount|all>")
    won = random.random() < 0.5
    if won:
        storage.change_balance(user.id, bet)
        await message.reply_text(f"🪙 Heads! You won {bet} coins.")
    else:
        storage.change_balance(user.id, -bet)
        await message.reply_text(f"🪙 Tails! You lost {bet} coins.")


async def dice_cmd(client: Client, message: Message):
    user = message.from_user
    bal, _ = storage.get_balance(user.id)
    bet = _parse_bet(message.command[1:], bal)
    if bet is None or bet <= 0 or bet > bal:
        return await message.reply_text("Usage: /dice <amount|all>  (roll 4-6 to win 2x)")
    roll = random.randint(1, 6)
    if roll >= 4:
        storage.change_balance(user.id, bet)
        await message.reply_text(f"🎲 Rolled {roll}. You won {bet} coins!")
    else:
        storage.change_balance(user.id, -bet)
        await message.reply_text(f"🎲 Rolled {roll}. You lost {bet} coins.")


SLOT_SYMBOLS = ["🍒", "🍋", "🍇", "🔔", "⭐", "7️⃣"]


async def slots_cmd(client: Client, message: Message):
    user = message.from_user
    bal, _ = storage.get_balance(user.id)
    bet = _parse_bet(message.command[1:], bal)
    if bet is None or bet <= 0 or bet > bal:
        return await message.reply_text("Usage: /slots <amount|all>")
    spin = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    display = " | ".join(spin)
    if spin[0] == spin[1] == spin[2]:
        payout = bet * 5
        storage.change_balance(user.id, payout)
        await message.reply_text(f"🎰 {display}\nJACKPOT! You won {payout} coins!")
    elif len(set(spin)) == 2:
        payout = bet
        storage.change_balance(user.id, payout)
        await message.reply_text(f"🎰 {display}\nNice! You won {payout} coins.")
    else:
        storage.change_balance(user.id, -bet)
        await message.reply_text(f"🎰 {display}\nYou lost {bet} coins.")


def register(app: Client):
    app.add_handler(MessageHandler(coinflip_cmd, filters.command("coinflip")))
    app.add_handler(MessageHandler(dice_cmd, filters.command("dice")))
    app.add_handler(MessageHandler(slots_cmd, filters.command("slots")))
