"""
seed_db.py — Load vote_records.json into the SQLite database.

Usage:
    python scripts/seed_db.py data/vote_records.json
"""

import asyncio
import json
import os
import sys

import aiosqlite

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "votes.db"))


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_db.py <vote_records.json>")
        sys.exit(1)

    json_path = sys.argv[1]

    with open(json_path) as f:
        records = json.load(f)

    print(f"Loading {len(records)} records into {DB_PATH}")

    async with aiosqlite.connect(DB_PATH) as db:
        # Create tables if needed
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
            """
        )

        # Insert vote records
        for rec in records:
            # Each record should have votes: { member_name: "yes/no/abstain/absent" }
            votes = rec.get("votes", {})
            for member_name, vote_val in votes.items():
                # Ensure member exists
                await db.execute(
                    "INSERT OR IGNORE INTO members (name) VALUES (?)",
                    (member_name,),
                )
                await db.execute(
                    "INSERT INTO votes (date, item_number, item_title, member_name, vote) VALUES (?, ?, ?, ?, ?)",
                    (
                        rec.get("date", ""),
                        rec.get("item_number", ""),
                        rec.get("item_title", ""),
                        member_name,
                        vote_val.lower(),
                    ),
                )

        await db.commit()

        # Report
        row = await db.execute("SELECT COUNT(*) FROM votes")
        vote_count = (await row.fetchone())[0]
        row = await db.execute("SELECT COUNT(*) FROM members")
        member_count = (await row.fetchone())[0]

        print(f"✓ Seeded {vote_count} votes for {member_count} members")


if __name__ == "__main__":
    asyncio.run(main())
