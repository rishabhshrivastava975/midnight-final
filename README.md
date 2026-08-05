# Midnight

One Telegram bot, one framework (Pyrogram), one process — combining:

- 🎵 **Music / VC** — `/play` `/skip` `/stop` `/queue` (voice-chat streaming via PyTgCalls + yt-dlp)
- 🛡 **Chat admin** — `/ban` `/unban` `/mute` `/unmute` `/promote` `/demote` `/warn` `/pin`
- 💰 **Economy & bank** — `/balance` `/daily` `/work` `/deposit` `/withdraw` `/pay` `/leaderboard`
- 🎰 **Minigames & casino** — `/coinflip` `/dice` `/slots` (play-money coins only, not real currency)
- 🤖 **AI & utilities** — `/ask` `/calc` `/id`
- 🎌 **Anime actions** — `/hug` `/pat` `/slap` `/poke` `/cuddle` `/kiss` `/wave` `/highfive`
- 🎨 **Theme manager** — `/theme` `/settheme`
- 👑 **Sudo & owner** — `/addsudo` `/delsudo` `/sudolist` `/broadcast`

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` → `.env` and fill in:
   - `API_ID` / `API_HASH` from https://my.telegram.org
   - `BOT_TOKEN` from @BotFather
   - `STRING_SESSION` — a userbot session for the "assistant" account that
     actually joins voice chats (bots can't join VCs directly). Generate this
     yourself with a throwaway account, e.g.:
     ```python
     from pyrogram import Client
     with Client("gen", api_id=..., api_hash=...) as app:
         print(app.export_session_string())
     ```
     Never share or commit this string — it's equivalent to a full login token.
   - `OWNER_ID` — your numeric Telegram user ID
   - `SUDO_USERS` — comma-separated user IDs with elevated (non-owner) access
   - `ANTHROPIC_API_KEY` — optional, only needed for `/ask`
3. Add both the bot and the assistant account to your group.
4. `python main.py`

## Deploying on Heroku

Heroku dynos have an **ephemeral filesystem** — anything written to disk
(including the SQLite `midnight_bot.db`) is wiped on every restart, and
dynos restart automatically at least once a day, plus on every deploy. That
means balances, warns, themes, and sudo users **will periodically reset**
if you leave storage as SQLite on Heroku. For a Heroku deployment that
actually needs to keep that data, swap `storage.py` to use Heroku Postgres
(a free-tier add-on) instead — happy to do that port if you want it.

Steps:

1. `heroku create your-app-name`
2. `heroku buildpacks:add heroku-community/apt` then `heroku buildpacks:add heroku/python`
   (the `Aptfile` in this repo installs `ffmpeg`, which PyTgCalls needs for
   voice-chat audio — Heroku doesn't include it by default)
3. Set config vars instead of `.env` (Heroku doesn't read `.env` files):
   ```
   heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... STRING_SESSION=... OWNER_ID=... SUDO_USERS=... ANTHROPIC_API_KEY=...
   ```
4. `git push heroku main`
5. This bot doesn't serve HTTP, so it runs as a **worker** dyno, not `web`:
   ```
   heroku ps:scale web=0 worker=1
   ```
   (the `Procfile` already declares `worker: python main.py`)
6. `heroku logs --tail` to confirm it started up.

`app.json` is included too, if you'd rather set this up via Heroku's
"Deploy to Heroku" button / Heroku Pipelines UI instead of the CLI.

## Notes

- **Storage**: SQLite (`midnight_bot.db`), created automatically on first run.
  Holds balances, warns, per-chat themes, and persisted sudo users.
- **Music source**: `/play` resolves songs via yt-dlp and streams them into
  the voice chat. That's the common pattern for these bots, but it's worth
  knowing it isn't licensed distribution — fine for a private/personal group,
  but not something to run as a public service without paying attention to
  copyright. If you'd rather stay clearly on the licensed side, swap
  `modules/music.py`'s source for Spotify's 30-second preview clips, your own
  uploaded audio files, or a Creative Commons library — ask and I can build
  whichever of those you want.
- **Casino module** uses in-bot play-money coins from the economy system —
  no real currency involved.
