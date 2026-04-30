import sqlite3
import asyncio
from datetime import datetime, timedelta
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_active TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            required INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            category TEXT,
            prompt TEXT,
            reference_image BLOB,
            generated_image BLOB,
            generation_type TEXT,
            created_at TEXT
        )
    """)

    default_settings = [
        ("welcome_text", "AZIK AI BOT ga xush kelibsiz! 🤖\nSun'iy intellekt yordamida ishlang."),
        ("subscription_text", "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:"),
    ]

    for key, value in default_settings:
        cursor.execute(
            "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    conn.commit()
    conn.close()


def upsert_user(user_id: int, username: str, first_name: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO users (id, username, first_name, last_active)
        VALUES (?, ?, ?, ?)

        ON CONFLICT(id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_active=excluded.last_active
        """,

        (
            user_id,
            username or "",
            first_name or "",
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM users ORDER BY last_active DESC"
    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_user_count():
    conn = get_connection()

    count = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    conn.close()

    return count


def get_active_users(days: int):

    conn = get_connection()

    since = (
        datetime.now() - timedelta(days=days)
    ).isoformat()

    count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE last_active >= ?",
        (since,)
    ).fetchone()[0]

    conn.close()

    return count


def get_channels():

    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM channels"
    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def get_required_channels():

    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM channels WHERE required=1"
    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def add_channel(name: str, link: str, required: bool = True):

    conn = get_connection()

    conn.execute(
        "INSERT INTO channels (name, link, required) VALUES (?, ?, ?)",
        (name, link, 1 if required else 0)
    )

    conn.commit()
    conn.close()


def delete_channel(channel_id: int):

    conn = get_connection()

    conn.execute(
        "DELETE FROM channels WHERE id=?",
        (channel_id,)
    )

    conn.commit()
    conn.close()


def get_setting(key: str) -> str:

    conn = get_connection()

    row = conn.execute(
        "SELECT value FROM bot_settings WHERE key=?",
        (key,)
    ).fetchone()

    conn.close()

    return row["value"] if row else ""


def set_setting(key: str, value: str):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO bot_settings (key, value)

        VALUES (?, ?)

        ON CONFLICT(key)
        DO UPDATE SET value=excluded.value
        """,

        (key, value)
    )

    conn.commit()
    conn.close()