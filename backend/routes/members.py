from fastapi import APIRouter
from backend.database import get_db

router = APIRouter()


@router.get("")
async def list_members():
    """Return all council members."""
    db = await get_db()
    try:
        rows = await db.execute("SELECT * FROM members ORDER BY district")
        results = await rows.fetchall()
        return [dict(r) for r in results]
    finally:
        await db.close()


@router.get("/{member_id}/profile")
async def member_profile(member_id: int):
    """Return a member's vote history, policy breakdown, and agreement rates."""
    db = await get_db()
    try:
        # Basic member info
        row = await db.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = await row.fetchone()
        if not member:
            return {"error": "Member not found"}
        member = dict(member)

        name = member["name"]

        # Vote history
        rows = await db.execute(
            """SELECT v.date, v.item_number, v.item_title, v.vote,
                      pt.tag, pt.summary
               FROM votes v
               LEFT JOIN policy_tags pt ON v.item_title = pt.item_title
               WHERE v.member_name = ?
               ORDER BY v.date DESC""",
            (name,),
        )
        votes = [dict(r) for r in await rows.fetchall()]

        # Policy breakdown (% yes by tag)
        rows = await db.execute(
            """SELECT pt.tag,
                      COUNT(*) as total,
                      SUM(CASE WHEN v.vote='yes' THEN 1 ELSE 0 END) as yes_count
               FROM votes v
               JOIN policy_tags pt ON v.item_title = pt.item_title
               WHERE v.member_name = ?
               GROUP BY pt.tag""",
            (name,),
        )
        breakdown = []
        for r in await rows.fetchall():
            r = dict(r)
            breakdown.append({
                "tag": r["tag"],
                "total": r["total"],
                "yes_count": r["yes_count"],
                "yes_pct": round(r["yes_count"] / r["total"] * 100, 1) if r["total"] > 0 else 0,
            })

        # Agreement rates with other members
        rows = await db.execute(
            """SELECT m2.member_name as other_member,
                      COUNT(*) as shared_votes,
                      SUM(CASE WHEN m1.vote = m2.vote THEN 1 ELSE 0 END) as agree_count
               FROM votes m1
               JOIN votes m2 ON m1.item_title = m2.item_title AND m1.date = m2.date
               WHERE m1.member_name = ? AND m2.member_name != ?
               GROUP BY m2.member_name""",
            (name, name),
        )
        agreements = []
        for r in await rows.fetchall():
            r = dict(r)
            agreements.append({
                "member": r["other_member"],
                "shared_votes": r["shared_votes"],
                "agree_count": r["agree_count"],
                "agree_pct": round(r["agree_count"] / r["shared_votes"] * 100, 1) if r["shared_votes"] > 0 else 0,
            })

        return {
            **member,
            "votes": votes,
            "policy_breakdown": breakdown,
            "agreement_rates": sorted(agreements, key=lambda x: x["agree_pct"], reverse=True),
        }
    finally:
        await db.close()
