from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Body
from app.api.rag_service import rag_service
from app.services.db import db_service
from app.crawler.scheduler import trigger_immediate_sync

router = APIRouter(prefix="/api", tags=["Intelligence API"])

class ChatRequest(BaseModel):
    message: Optional[str] = None
    prompt: Optional[str] = None
    query: Optional[str] = None
    session_id: Optional[str] = None
    language: Optional[str] = "ar"
    lang: Optional[str] = None

class CrawlNowRequest(BaseModel):
    url: Optional[str] = None

@router.post("/chat")
@router.post("/v1/chat")
async def chat_endpoint(payload: ChatRequest = Body(...)):
    """
    POST /api/chat & /api/v1/chat:
    Receives { message/prompt/query, session_id, language }.
    Returns { reply, sources: [{ title, url }], session_id }.
    """
    query_text = payload.message or payload.prompt or payload.query or ""

    student_lang = payload.language or payload.lang or "ar"

    result = rag_service.answer_query(
        message=query_text,
        session_id=payload.session_id,
        language=student_lang
    )

    return {
        "reply": result["reply"],
        "answer": result["reply"],
        "source_url": result.get("source_url"),
        "sources": result.get("sources", []),
        "session_id": result["session_id"]
    }

@router.get("/history/{session_id}")
@router.get("/chat/history/{session_id}")
def get_chat_history_endpoint(session_id: str):
    """
    GET /api/history/{session_id}:
    Returns past messages for the conversation from MongoDB chat_history collection.
    """
    record = db_service.get_chat_history(session_id)
    if not record:
        return {"session_id": session_id, "messages": [], "student_language": "ar"}
    return {
        "session_id": session_id,
        "messages": record.get("messages", []),
        "student_language": record.get("student_language", "ar")
    }

@router.post("/admin/crawl-now")
@router.post("/admin/trigger-crawl")
async def trigger_crawl_now_endpoint(payload: Optional[CrawlNowRequest] = Body(None)):
    """
    POST /api/admin/crawl-now:
    Triggers immediate re-indexing of university URLs.
    """
    results = await trigger_immediate_sync()
    return {
        "status": "success",
        "message": "Immediate university URL crawl & SHA-256 re-indexing completed.",
        "results": results
    }

@router.get("/admin/crawl-stats")
@router.get("/admin/crawl-status")
def get_crawl_stats_endpoint():
    """
    GET /api/admin/crawl-stats:
    Returns count of indexed pages and last check timestamp from MongoDB crawled_sources collection.
    """
    sources = db_service.list_crawled_sources()
    indexed_pages_count = len(sources)

    timestamps = [s.get("last_crawled") or s.get("last_scraped_at") for s in sources if (s.get("last_crawled") or s.get("last_scraped_at"))]
    last_check_timestamp = max(timestamps) if timestamps else "Never checked"

    return {
        "indexed_pages_count": indexed_pages_count,
        "last_check_timestamp": last_check_timestamp,
        "sources": sources
    }
