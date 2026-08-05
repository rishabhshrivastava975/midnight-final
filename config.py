import os

# ---- REQUIRED: fill these in your .env file (see .env.example) ----
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
STRING_SESSION = os.getenv("STRING_SESSION", "")  # userbot session, needed for voice chats

OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # your Telegram numeric user id

# Comma separated list of sudo user ids, e.g. "111111,222222"
SUDO_USERS = set(
    int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip().isdigit()
)

# Optional: Anthropic API key for the /ask AI command
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DB_PATH = os.getenv("DB_PATH", "midnight_bot.db")

BOT_NAME = "Midnight"
