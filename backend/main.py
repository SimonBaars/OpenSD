import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routes.votes import router as votes_router
from backend.routes.members import router as members_router
from backend.routes.heatmap import router as heatmap_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="SD Council Voting Pattern Dashboard",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server and production frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Also allow a configured production origin
prod_origin = os.getenv("FRONTEND_ORIGIN")
if prod_origin:
    origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(votes_router, prefix="/votes", tags=["votes"])
app.include_router(members_router, prefix="/members", tags=["members"])
app.include_router(heatmap_router, prefix="/heatmap", tags=["heatmap"])


@app.get("/health")
async def health():
    return {"status": "ok"}
