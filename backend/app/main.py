from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.crawler.scheduler import start_crawler_scheduler, trigger_immediate_sync
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background APScheduler crawler scanner
    start_crawler_scheduler()
    try:
        await trigger_immediate_sync()
    except Exception as e:
        print(f"[Startup Warning] Initial crawler sync failed: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Unified API Routes (POST /api/chat, GET /api/history/{session_id}, POST /api/admin/crawl-now, GET /api/admin/crawl-stats)
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "university": "University of Jordan",
        "branch": "Aqaba Branch (فرع العقبة)",
        "project": settings.PROJECT_NAME,
        "mode": "Pure Text-Based Chat Interface (Zero Audio / Zero SQL)",
        "architecture": "MongoDB Document Store + ChromaDB Vector Index + Autonomous Web Ingestion Engine"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "UJ Aqaba AI Academic Assistant",
        "database": "MongoDB / ChromaDB Online"
    }

