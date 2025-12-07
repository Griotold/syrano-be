import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import rizz, auth, billing

logger = logging.getLogger("syrano")
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    yield  # <-- 여기까지가 startup, 여기서부터는 앱이 돌아가는 동안

    # shutdown (필요하면 연결 정리, 리소스 반환 등 여기에)
    logger.info("Shutting down Syrano API...")

app = FastAPI(title="Syrano API", lifespan=lifespan)

# CORS 설정 (개발 단계라 일단 * 허용, 운영에서 좁히면 됨)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # TODO: 운영에서는 실제 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rizz.router, prefix="/rizz", tags=["rizz"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])