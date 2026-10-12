import hashlib
import datetime
from typing import Dict, Any, List
from app.services.db import db_service
from app.services.vector_service import vector_service
from app.crawler.scraper import scraper

class SHA256ChangeDetector:
    """SHA-256 Content Hashing & Automated Change Detection Engine."""

    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def sync_page_data(self, url: str, scraped_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculates SHA-256 hash of core content, checks MongoDB baseline,
        and triggers ChromaDB re-indexing if content altered.
        """
        if not scraped_data:
            scraped_data = await scraper.scrape_url(url)
            if not scraped_data:
                return {"url": url, "status": "failed", "reason": "Scrape failed or page unreachable"}

        clean_text = scraped_data.get("clean_text", "")
        new_hash = self.compute_sha256(clean_text)

        # Retrieve baseline record from MongoDB crawled_sources collection
        existing_doc = db_service.get_crawled_source(url)
        old_hash = existing_doc.get("content_hash") if existing_doc else None

        # Check if content has changed
        if old_hash == new_hash:
            return {
                "url": url,
                "status": "unchanged",
                "content_hash": new_hash,
                "message": "Content hash matches existing MongoDB record. Skipped re-indexing."
            }

        now_str = datetime.datetime.utcnow().isoformat()
        category = scraped_data.get("category") or scraped_data.get("section_category") or "general_portal"
        title = scraped_data.get("title", "University of Jordan Page")
        is_static_bylaw = (category == "bylaw" or "reg" in url.lower() or "admissions" in url.lower())

        # 1. Update MongoDB NoSQL crawled_sources record
        db_service.upsert_crawled_source(
            url=url,
            title=title,
            category=category,
            content_hash=new_hash,
            last_crawled=now_str,
            is_static_bylaw=is_static_bylaw
        )

        # 2. Chunk updated text content
        chunks = vector_service.chunk_text(clean_text)
        metadatas = []

        for idx, chunk in enumerate(chunks):
            metadatas.append({
                "url": url,
                "source_url": url,
                "title": title,
                "category": category,
                "is_static_bylaw": is_static_bylaw,
                "chunk_index": idx,
                "updated_at": now_str
            })

        # 3. Atomic update embeddings in ChromaDB vector store
        vector_service.update_page_embeddings(
            url=url,
            new_chunks=chunks,
            metadatas=metadatas,
            category=category
        )

        return {
            "url": url,
            "status": "updated",
            "content_hash": new_hash,
            "category": category,
            "chunks_count": len(chunks),
            "message": "SHA-256 diff detected. Updated MongoDB metadata and ChromaDB vector index."
        }

change_detector = SHA256ChangeDetector()
