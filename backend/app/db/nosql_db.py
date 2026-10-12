import os
import hashlib
from typing import Dict, Any, List, Optional
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

class MemoryDocumentStore:
    """In-memory NoSQL Document Store fallback when MongoDB instance is not connected."""
    def __init__(self):
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def _get_coll(self, name: str) -> Dict[str, Dict[str, Any]]:
        if name not in self._collections:
            self._collections[name] = {}
        return self._collections[name]

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        coll = self._get_coll(collection_name)
        for doc in coll.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc.copy()
        return None

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = True):
        coll = self._get_coll(collection_name)
        existing_key = None
        for key, doc in coll.items():
            if all(doc.get(k) == v for k, v in query.items()):
                existing_key = key
                break

        doc_data = update.get("$set", update)
        if existing_key:
            coll[existing_key].update(doc_data)
        elif upsert:
            doc_id = query.get("url") or query.get("_id") or str(len(coll) + 1)
            new_doc = {**query, **doc_data}
            coll[doc_id] = new_doc

    def find_all(self, collection_name: str) -> List[Dict[str, Any]]:
        coll = self._get_coll(collection_name)
        return [doc.copy() for doc in coll.values()]

class MongoDBManager:
    """Zero-SQL MongoDB / Document Store interface for metadata and crawled state."""
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
                # Quick ping test
                self.client.admin.command('ping')
                self.db = self.client[self.db_name]
                self.use_mongo = True
            except Exception:
                self.use_mongo = False

    def get_collection(self, collection_name: str = "crawled_sources"):
        if self.use_mongo and self.db is not None:
            return self.db[collection_name]
        return None

    def get_source_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return self.db["crawled_sources"].find_one({"url": url})
        return self.memory_store.find_one("crawled_sources", {"url": url})

    def save_crawled_source(self, url: str, data: Dict[str, Any]):
        if self.use_mongo and self.db is not None:
            self.db["crawled_sources"].update_one(
                {"url": url},
                {"$set": data},
                upsert=True
            )
        else:
            self.memory_store.update_one("crawled_sources", {"url": url}, data, upsert=True)

    def get_all_crawled_sources(self) -> List[Dict[str, Any]]:
        if self.use_mongo and self.db is not None:
            return list(self.db["crawled_sources"].find({}, {"_id": 0}))
        return self.memory_store.find_all("crawled_sources")

db_manager = MongoDBManager()
