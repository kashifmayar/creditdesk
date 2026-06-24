import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, engine
from app.routers import auth, borrowers, policy, policy_upload, reminders

logger = logging.getLogger(__name__)

app = FastAPI(title="Credit Analyst API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    from app.seed import seed_if_empty

    await seed_if_empty()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(policy.router, prefix="/policy", tags=["policy"])
app.include_router(policy_upload.router, prefix="/policy", tags=["policy-upload"])
app.include_router(borrowers.router, prefix="/borrowers", tags=["borrowers"])
app.include_router(reminders.router, prefix="/reminders", tags=["reminders"])


@app.get("/health")
async def health():
    return {"status": "ok"}
