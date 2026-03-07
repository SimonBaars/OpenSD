from fastapi import APIRouter
from backend.database import get_db

router = APIRouter()


@router.get("")
async def alliance_matrix():
    """Compute pairwise agreement % for all member pairs."""
    db = await get_db()
    try:
        rows = await db.execute(
            """SELECT m1.member_name as member_a,
                      m2.member_name as member_b,
                      COUNT(*) as shared_votes,
                      SUM(CASE WHEN m1.vote = m2.vote THEN 1 ELSE 0 END) as agree_count
               FROM votes m1
               JOIN votes m2 ON m1.item_title = m2.item_title
                            AND m1.date = m2.date
                            AND m1.member_name < m2.member_name
               GROUP BY m1.member_name, m2.member_name"""
        )
        results = []
        for r in await rows.fetchall():
            r = dict(r)
            results.append({
                "member_a": r["member_a"],
                "member_b": r["member_b"],
                "shared_votes": r["shared_votes"],
                "agree_count": r["agree_count"],
                "agree_pct": round(r["agree_count"] / r["shared_votes"] * 100, 1) if r["shared_votes"] > 0 else 0,
            })
        return results
    finally:
        await db.close()
