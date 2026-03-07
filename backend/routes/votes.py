from fastapi import APIRouter, Query
from typing import Optional
from backend.database import get_db

router = APIRouter()


@router.get("")
async def list_votes(
    member: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, alias="dateFrom"),
    date_to: Optional[str] = Query(None, alias="dateTo"),
):
    """Return vote records, optionally filtered."""
    db = await get_db()
    try:
        query = """
            SELECT v.id, v.date, v.item_number, v.item_title,
                   v.member_name, v.vote,
                   pt.tag, pt.summary
            FROM votes v
            LEFT JOIN policy_tags pt ON v.item_title = pt.item_title
            WHERE 1=1
        """
        params: list = []

        if member:
            query += " AND v.member_name = ?"
            params.append(member)
        if tag:
            query += " AND pt.tag = ?"
            params.append(tag)
        if date_from:
            query += " AND v.date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND v.date <= ?"
            params.append(date_to)

        query += " ORDER BY v.date DESC, v.item_number"

        rows = await db.execute(query, params)
        results = await rows.fetchall()
        return [dict(r) for r in results]
    finally:
        await db.close()
