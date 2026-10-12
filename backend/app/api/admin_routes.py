from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Body
from app.crawler.sync_manager import sync_manager
from app.db.mongo_client import mongo_client

admin_router = APIRouter(prefix="/api/admin", tags=["Admin Crawler"])

class CrawlTriggerRequest(BaseModel):
    target_url: Optional[str] = None

@admin_router.post("/trigger-crawl")
async def trigger_crawl_endpoint(payload: Optional[CrawlTriggerRequest] = Body(None)):
    """
    POST /api/admin/trigger-crawl:
    Manually trigger the autonomous university web crawler for a specific URL or full re-sync.
    """
    target_url = payload.target_url if payload else None
    
    if target_url:
        result = await sync_manager.sync_url(target_url)
        return {
            "status": "success",
            "type": "single_url_sync",
            "target_url": target_url,
            "results": [result]
        }
    else:
        results = await sync_manager.run_full_sync()
        return {
            "status": "success",
            "type": "full_portal_sync",
            "total_synced": len(results),
            "results": results
        }

@admin_router.get("/crawl-status")
def get_crawl_status_endpoint():
    """
    GET /api/admin/crawl-status:
    Returns total indexed pages, last sync timestamp, and list of detected webpage updates.
    """
    sources = mongo_client.list_crawled_sources()
    indexed_pages_count = len(sources)

    timestamps = [s.get("last_scraped_at") for s in sources if s.get("last_scraped_at")]
    last_sync_timestamp = max(timestamps) if timestamps else "Not synced yet"

    detected_updates = [
        {
            "url": s.get("url"),
            "title": s.get("title"),
            "section_category": s.get("section_category"),
            "content_hash": s.get("content_hash"),
            "last_scraped_at": s.get("last_scraped_at"),
            "status": s.get("status")
        }
        for s in sources
    ]

    return {
        "indexed_pages_count": indexed_pages_count,
        "last_sync_timestamp": last_sync_timestamp,
        "detected_updates": detected_updates,
        "sources": sources
    }
