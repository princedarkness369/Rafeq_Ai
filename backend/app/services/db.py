import os
import datetime
from typing import Dict, Any, List, Optional
from app.config import settings

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

class MemoryDocumentStore:
    """In-memory NoSQL Document Store fallback when MongoDB daemon is disconnected."""
    def __init__(self):
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {
            "crawled_sources": {},
            "chat_history": {}
        }

    def _coll(self, name: str) -> Dict[str, Dict[str, Any]]:
        if name not in self._collections:
            self._collections[name] = {}
        return self._collections[name]

    def find_one(self, coll_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        coll = self._coll(coll_name)
        for doc in coll.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc.copy()
        return None

    def update_one(self, coll_name: str, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = True):
        coll = self._coll(coll_name)
        existing_key = None
        for key, doc in coll.items():
            if all(doc.get(k) == v for k, v in query.items()):
                existing_key = key
                break

        doc_data = update.get("$set", update)
        if existing_key:
            coll[existing_key].update(doc_data)
        elif upsert:
            doc_id = query.get("url") or query.get("session_id") or str(len(coll) + 1)
            coll[doc_id] = {**query, **doc_data}

    def find_all(self, coll_name: str) -> List[Dict[str, Any]]:
        return [doc.copy() for doc in self._coll(coll_name).values()]

class DatabaseService:
    """MongoDB Document Store Manager for Crawled Sources & Chat History."""

    def __init__(self):
        self.mongo_uri = settings.MONGO_URI or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = settings.MONGO_DB_NAME or os.getenv("MONGO_DB_NAME", "uj_academic_assistant")
        self.client = None
        self.db = None
        self.memory_store = MemoryDocumentStore()
        self.use_mongo = False

        if PYMONGO_AVAILABLE:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                self.client.admin.command("ping")
                self.db = self.client[self.db_name]
                self.use_mongo = True
            except Exception:
                self.use_mongo = False

    # 1. Collection crawled_sources
    # Schema: { url, title, category, content_hash, last_crawled, is_static_bylaw }
    def upsert_crawled_source(
        self,
        url: str,
        title: str,
        category: str,
        content_hash: str,
        last_crawled: str = None,
        is_static_bylaw: bool = False
    ):
        if not last_crawled:
            last_crawled = datetime.datetime.utcnow().isoformat()

        doc_data = {
            "url": url,
            "title": title,
            "category": category,
            "section_category": category,
            "content_hash": content_hash,
            "last_crawled": last_crawled,
            "last_scraped_at": last_crawled,
            "is_static_bylaw": is_static_bylaw,
            "is_baseline_bylaw": is_static_bylaw,
            "status": "synced"
        }

        if self.use_mongo and self.db is not None:
            self.db["crawled_sources"].update_one(
                {"url": url},
                {"$set": doc_data},
                upsert=True
            )
        else:
            self.memory_store.update_one("crawled_sources", {"url": url}, doc_data, upsert=True)

    def get_crawled_source(self, url: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return self.db["crawled_sources"].find_one({"url": url}, {"_id": 0})
        return self.memory_store.find_one("crawled_sources", {"url": url})

    def list_crawled_sources(self) -> List[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return list(self.db["crawled_sources"].find({}, {"_id": 0}))
        return self.memory_store.find_all("crawled_sources")

    # 2. Collection chat_history
    # Schema: { session_id, messages: [{ role, content, timestamp }], student_language }
    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        student_language: str = "ar"
    ):
        existing = self.get_chat_history(session_id)
        messages = existing.get("messages", []) if existing else []
        
        msg_entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        messages.append(msg_entry)

        doc_data = {
            "session_id": session_id,
            "student_language": student_language,
            "messages": messages,
            "updated_at": datetime.datetime.utcnow().isoformat()
        }

        if self.use_mongo and self.db is not None:
            self.db["chat_history"].update_one(
                {"session_id": session_id},
                {"$set": doc_data},
                upsert=True
            )
        else:
            self.memory_store.update_one("chat_history", {"session_id": session_id}, doc_data, upsert=True)

    def get_chat_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return self.db["chat_history"].find_one({"session_id": session_id}, {"_id": 0})
        return self.memory_store.find_one("chat_history", {"session_id": session_id})

db_service = DatabaseService()
