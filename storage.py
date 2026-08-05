import sqlite3
import time
from contextlib import contextmanager
from config import DB_PATH

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            last_daily INTEGER DEFAULT 0,
            last_work INTEGER DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS warns (
            chat_id INTEGER,
            user_id INTEGER,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS themes (
            chat_id INTEGER PRIMARY KEY,
            theme_name TEXT DEFAULT 'default'
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS sudo_users (
            user_id INTEGER PRIMARY KEY
        )""")
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

# ---------- Economy ----------
def ensure_user(user_id: int):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def get_balance(user_id: int):
    ensure_user(user_id)
    with get_conn() as conn:
        row = conn.execute("SELECT balance, bank FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row  # (balance, bank)

def change_balance(user_id: int, amount: int):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
        conn.commit()

def change_bank(user_id: int, amount: int):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute("UPDATE users SET bank = bank + ? WHERE user_id=?", (amount, user_id))
        conn.commit()

def transfer(from_id: int, to_id: int, amount: int) -> bool:
    ensure_user(from_id)
    ensure_user(to_id)
    with get_conn() as conn:
        bal = conn.execute("SELECT balance FROM users WHERE user_id=?", (from_id,)).fetchone()[0]
        if bal < amount:
            return False
        conn.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, from_id))
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, to_id))
        conn.commit()
        return True

def get_last(user_id: int, field: str):
    ensure_user(user_id)
    with get_conn() as conn:
        row = conn.execute(f"SELECT {field} FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row[0]

def set_last(user_id: int, field: str, ts: int):
    ensure_user(user_id)
    with get_conn() as conn:
        conn.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (ts, user_id))
        conn.commit()

def leaderboard(limit=10):
    with get_conn() as conn:
        return conn.execute(
            "SELECT user_id, balance + bank as total FROM users ORDER BY total DESC LIMIT ?",
            (limit,)
        ).fetchall()

# ---------- Warns ----------
def add_warn(chat_id: int, user_id: int) -> int:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO warns (chat_id, user_id, count) VALUES (?, ?, 1) "
            "ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1",
            (chat_id, user_id)
        )
        conn.commit()
        row = conn.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)
        ).fetchone()
        return row[0]

def reset_warns(chat_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        conn.commit()

# ---------- Theme ----------
def set_theme(chat_id: int, theme_name: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO themes (chat_id, theme_name) VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET theme_name=excluded.theme_name",
            (chat_id, theme_name)
        )
        conn.commit()

def get_theme(chat_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT theme_name FROM themes WHERE chat_id=?", (chat_id,)).fetchone()
        return row[0] if row else "default"

# ---------- Sudo (persisted, in addition to config.SUDO_USERS) ----------
def add_sudo(user_id: int):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO sudo_users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def del_sudo(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM sudo_users WHERE user_id=?", (user_id,))
        conn.commit()

def list_sudo():
    with get_conn() as conn:
        return [r[0] for r in conn.execute("SELECT user_id FROM sudo_users").fetchall()]
