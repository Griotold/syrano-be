import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import init_db
from app.routers import rizz, auth

logger = logging.getLogger("syrano")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Syrano API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    yield  # <-- 여기까지가 startup, 여기서부터는 앱이 돌아가는 동안

    # shutdown (필요하면 연결 정리, 리소스 반환 등 여기에)
    logger.info("Shutting down Syrano API...")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rizz.router, prefix="/rizz", tags=["rizz"])