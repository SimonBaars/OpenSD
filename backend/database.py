import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "votes.db"))


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                district INTEGER,
                photo_url TEXT,
                ai_summary TEXT
            );

            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                item_number TEXT,
                item_title TEXT NOT NULL,
                member_name TEXT NOT NULL,
                vote TEXT NOT NULL CHECK(vote IN ('yes','no','abstain','absent')),
                FOREIGN KEY (member_name) REFERENCES members(name)
            );

            CREATE TABLE IF NOT EXISTS policy_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_title TEXT NOT NULL UNIQUE,
                tag TEXT NOT NULL,
                summary TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_votes_member ON votes(member_name);
            CREATE INDEX IF NOT EXISTS idx_votes_date ON votes(date);
            CREATE INDEX IF NOT EXISTS idx_policy_tag ON policy_tags(tag);
            """
        )
        await db.commit()
