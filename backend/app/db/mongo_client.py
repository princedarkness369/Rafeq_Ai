import os
import datetime
from typing import Dict, Any, List, Optional
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

class MemoryDocumentStore:
    """In-memory NoSQL Document Store fallback when MongoDB daemon is not running."""
    def __init__(self):
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {
            "crawled_sources": {},
            "chat_sessions": {}
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

class MongoClientManager:
    """MongoDB Client & Document Store for Metadata and Chat Sessions."""
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "uj_academic_assistant")
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
    def upsert_crawled_source(
        self,
        url: str,
        title: str,
        section_category: str,
        content_hash: str,
        last_scraped_at: str = None,
        status: str = "synced",
        is_baseline_bylaw: bool = False
    ):
        if not last_scraped_at:
            last_scraped_at = datetime.datetime.utcnow().isoformat()

        doc_data = {
            "url": url,
            "title": title,
            "section_category": section_category,
            "content_hash": content_hash,
            "last_scraped_at": last_scraped_at,
            "status": status,
            "is_baseline_bylaw": is_baseline_bylaw
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

    # 2. Collection chat_sessions
    def create_chat_session(self, session_id: str, student_lang: str = "ar") -> Dict[str, Any]:
        now_str = datetime.datetime.utcnow().isoformat()
        session_doc = {
            "session_id": session_id,
            "student_lang": student_lang,
            "history": [],
            "created_at": now_str
        }
        if self.use_mongo and self.db is not None:
            self.db["chat_sessions"].update_one(
                {"session_id": session_id},
                {"$set": session_doc},
                upsert=True
            )
        else:
            self.memory_store.update_one("chat_sessions", {"session_id": session_id}, session_doc, upsert=True)
        return session_doc

    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return self.db["chat_sessions"].find_one({"session_id": session_id}, {"_id": 0})
        return self.memory_store.find_one("chat_sessions", {"session_id": session_id})

    def append_chat_message(self, session_id: str, role: str, message: str):
        existing = self.get_chat_session(session_id)
        if not existing:
            existing = self.create_chat_session(session_id)

        msg_entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        history = existing.get("history", [])
        history.append(msg_entry)

        if self.use_mongo and self.db is not None:
            self.db["chat_sessions"].update_one(
                {"session_id": session_id},
                {"$set": {"history": history}}
            )
        else:
            self.memory_store.update_one("chat_sessions", {"session_id": session_id}, {"history": history})

mongo_client = MongoClientManager()
