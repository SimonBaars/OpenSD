"""
classify_votes.py — Batch-classify vote items using Claude API.

Usage:
    python scripts/classify_votes.py

Reads untagged items from the SQLite DB and sends them to Claude for
policy classification. Writes results back to the policy_tags table.
"""

import asyncio
import os
import sys

import aiosqlite
from anthropic import Anthropic

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "votes.db"))

SYSTEM_PROMPT = """You are a policy classifier for San Diego City Council vote items.
Given a vote item title, classify it into exactly ONE of these categories:
Housing, Public Safety, Climate, Infrastructure, Budget, Transportation, Land Use, Health, Education, Other

Also provide a 1-sentence plain-English summary of what the item is about.

Respond in JSON format:
{"tag": "<category>", "summary": "<one sentence summary>"}

Only output valid JSON, nothing else."""

BATCH_SIZE = 20


def classify_batch(client: Anthropic, titles: list[str]) -> list[dict]:
    """Send a batch of item titles to Claude for classification."""
    prompt = "Classify each of the following San Diego City Council vote items:\n\n"
    for i, title in enumerate(titles, 1):
        prompt += f"{i}. {title}\n"
    prompt += "\nRespond with a JSON array of objects, one per item, in the same order."

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = response.content[0].text.strip()
    # Handle possible markdown code blocks
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY env var is not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get untagged item titles
        rows = await db.execute(
            """SELECT DISTINCT v.item_title
               FROM votes v
               LEFT JOIN policy_tags pt ON v.item_title = pt.item_title
               WHERE pt.id IS NULL"""
        )
        items = [dict(r)["item_title"] for r in await rows.fetchall()]

        if not items:
            print("All items are already classified!")
            return

        print(f"Found {len(items)} unclassified items")

        # Process in batches
        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i : i + BATCH_SIZE]
            print(f"  Classifying batch {i // BATCH_SIZE + 1} ({len(batch)} items)...")

            try:
                results = classify_batch(client, batch)
                for title, result in zip(batch, results):
                    await db.execute(
                        "INSERT OR REPLACE INTO policy_tags (item_title, tag, summary) VALUES (?, ?, ?)",
                        (title, result.get("tag", "Other"), result.get("summary", "")),
                    )
                await db.commit()
                print(f"    ✓ Classified {len(batch)} items")
            except Exception as e:
                print(f"    ✗ Error: {e}")

        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
