"""FastAPI server for OpenSD."""

import asyncio
import json
from pathlib import Path
from queue import Queue, Empty
from threading import Thread

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agent import SanDiegoAgent

app = FastAPI(title="OpenSD")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent.parent / "data"
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

agent = SanDiegoAgent()


HEARTBEAT_INTERVAL = 10  # seconds between keepalive pings

_SENTINEL = object()


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])

    async def generate():
        q: Queue = Queue()

        def _run():
            try:
                for event in agent.chat_stream(message, history):
                    q.put(event)
            except Exception as exc:
                q.put({"type": "error", "text": str(exc)})
            finally:
                q.put(_SENTINEL)

        thread = Thread(target=_run, daemon=True)
        thread.start()

        while True:
            try:
                event = await asyncio.to_thread(q.get, timeout=HEARTBEAT_INTERVAL)
            except Empty:
                yield ": heartbeat\n\n"
                continue
            if event is _SENTINEL:
                break
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/datasets")
async def datasets():
    """Return metadata for all loaded tables."""
    import duckdb

    con = duckdb.connect(str(agent.db_path), read_only=True)
    try:
        rows = con.execute(
            "SELECT table_name, dataset, row_count, columns FROM _metadata ORDER BY dataset"
        ).fetchall()
        return [
            {
                "table_name": r[0],
                "dataset": r[1],
                "row_count": r[2],
                "columns": json.loads(r[3]) if r[3] else [],
            }
            for r in rows
        ]
    finally:
        con.close()


@app.get("/api/boundaries/{name}")
async def boundaries(name: str):
    """Serve GeoJSON boundary files."""
    file_map = {
        "council_districts": DATA_DIR / "city-council-districts" / "council_districts_datasd.geojson",
        "community_plans": DATA_DIR / "community-planning-district-boundaries" / "cmty_plan_datasd.geojson",
        "police_beats": DATA_DIR / "police-beats" / "pd_beats_datasd.geojson",
        "street_segments": DATA_DIR / "streets-repair-segments" / "sd_paving_segs_datasd.geojson",
        "zoning": DATA_DIR / "zoning" / "zoning_datasd.geojson",
        "parks": DATA_DIR / "park-locations" / "parks_datasd.geojson",
    }
    path = file_map.get(name)
    if path and path.exists():
        return FileResponse(path, media_type="application/geo+json")
    return {"error": f"Boundary '{name}' not found. Available: {list(file_map.keys())}"}


# Serve frontend in production
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if any(seg.startswith(".") for seg in full_path.split("/")):
            return Response(status_code=404)
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
