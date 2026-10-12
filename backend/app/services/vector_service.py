import os
import uuid
import hashlib
from typing import List, Dict, Any, Optional
from app.config import settings

try:
    import chromadb  # type: ignore
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore
    LANGCHAIN_GEMINI_AVAILABLE = True
except ImportError:
    LANGCHAIN_GEMINI_AVAILABLE = False

try:
    from langchain_community.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    LANGCHAIN_SPLITTER_AVAILABLE = True
except ImportError:
    LANGCHAIN_SPLITTER_AVAILABLE = False

class DynamicVectorService:
    """ChromaDB Vector Store & Embedding Service with Metadata Filtering & Atomic Updates."""

    COLLECTION_BYLAWS = "bylaws_and_regulations"
    COLLECTION_DYNAMIC = "dynamic_news_and_events"

    def __init__(self):
        self.client = None
        self.collections: Dict[str, Any] = {}
        self.embedding_fn = None
        self._fallback_store: Dict[str, List[Dict[str, Any]]] = {
            self.COLLECTION_BYLAWS: [],
            self.COLLECTION_DYNAMIC: []
        }

        # Text Splitter preserving paragraph & table block structures
        if LANGCHAIN_SPLITTER_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", " | ", " ", ""]
            )
        else:
            self.text_splitter = None

        # Google Gemini Embeddings
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if LANGCHAIN_GEMINI_AVAILABLE and api_key:
            try:
                self.embedding_fn = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=api_key
                )
            except Exception as e:
                print(f"[VectorService Warning] Failed to init GoogleGenerativeAIEmbeddings: {e}")

        # ChromaDB Persistent Client
        if CHROMADB_AVAILABLE:
            try:
                persist_dir = settings.CHROMA_PERSIST_DIR or "./chroma_db"
                self.client = chromadb.PersistentClient(path=persist_dir)
                for name in [self.COLLECTION_BYLAWS, self.COLLECTION_DYNAMIC]:
                    self.collections[name] = self.client.get_or_create_collection(name=name)
            except Exception as e:
                print(f"[ChromaDB Warning] Fallback to Ephemeral Client: {e}")
                try:
                    self.client = chromadb.Client()
                    for name in [self.COLLECTION_BYLAWS, self.COLLECTION_DYNAMIC]:
                        self.collections[name] = self.client.get_or_create_collection(name=name)
                except Exception:
                    self.client = None

    def _get_target_collection_name(self, category: str) -> str:
        cat_lower = (category or "").lower()
        if "bylaw" in cat_lower or "rule" in cat_lower or "reg" in cat_lower or "scholarship" in cat_lower or "grade" in cat_lower:
            return self.COLLECTION_BYLAWS
        return self.COLLECTION_DYNAMIC

    def delete_by_url(self, url: str, category: Optional[str] = None):
        """Purge all vector embeddings for a given URL."""
        target_colls = [self._get_target_collection_name(category)] if category else [self.COLLECTION_BYLAWS, self.COLLECTION_DYNAMIC]
        for name in target_colls:
            if name in self.collections and self.collections[name] is not None:
                try:
                    self.collections[name].delete(where={"url": url})
                except Exception:
                    pass
            self._fallback_store[name] = [
                d for d in self._fallback_store[name]
                if d.get("metadata", {}).get("url") != url and d.get("metadata", {}).get("source_url") != url
            ]

    def update_page_embeddings(
        self,
        url: str,
        new_chunks: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None
    ):
        """
        Atomic Update Method:
        1. Deletes outdated embeddings for URL.
        2. Upserts new_chunks with metadata into vector store.
        """
        target_coll_name = self._get_target_collection_name(category)

        # 1. Purge existing vector embeddings for url
        self.delete_by_url(url, category=category)

        if not new_chunks:
            return

        # 2. Build metadata & document IDs
        if not metadatas:
            metadatas = []
            for idx in range(len(new_chunks)):
                metadatas.append({
                    "url": url,
                    "source_url": url,
                    "category": category or target_coll_name,
                    "chunk_index": idx
                })

        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
        ids = [f"{url_hash}_{idx}" for idx in range(len(new_chunks))]

        # 3. Upsert new chunks
        self.upsert_documents(
            category=category,
            texts=new_chunks,
            metadatas=metadatas,
            ids=ids
        )

    def upsert_documents(
        self,
        category: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        target_name = self._get_target_collection_name(category)
        if not ids:
            ids = [str(uuid.uuid4()) for _ in texts]

        for meta in metadatas:
            meta["category"] = target_name

        if target_name in self.collections and self.collections[target_name] is not None:
            try:
                self.collections[target_name].upsert(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            except Exception as e:
                print(f"[ChromaDB Upsert Warning]: {e}")
                for t, m, doc_id in zip(texts, metadatas, ids):
                    self._fallback_store[target_name].append({"id": doc_id, "text": t, "metadata": m})
        else:
            for t, m, doc_id in zip(texts, metadatas, ids):
                self._fallback_store[target_name].append({"id": doc_id, "text": t, "metadata": m})

    SIMILARITY_THRESHOLD = 0.45  # Cosine distance cutoff for ChromaDB

    def is_boilerplate_chunk(self, text: str) -> bool:
        if not text or len(text.strip()) < 15:
            return True
        t = text.lower()
        boilerplate_keywords = [
            "student registration", "نظام تسجيل الطلبة", "استعادة كلمة السر",
            "reset password", "microsoft account", "حساب مايكروسوفت",
            "دخول", "login.aspx", "log in", "sign in", "forget password", "نسيت كلمة السر"
        ]
        matches = sum(1 for kw in boilerplate_keywords if kw in t)
        if matches >= 2 or (matches >= 1 and len(text) < 160):
            return True
        return False

    def chunk_text(self, text: str) -> List[str]:
        """Split text while preserving table rows and section headers intact, skipping boilerplate."""
        raw_chunks = []
        if self.text_splitter:
            raw_chunks = self.text_splitter.split_text(text)
        else:
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            current = ""
            for p in paragraphs:
                if len(current) + len(p) > 500:
                    raw_chunks.append(current)
                    current = p
                else:
                    current = f"{current}\n{p}" if current else p
            if current:
                raw_chunks.append(current)
        
        # Filter out chrome / boilerplate chunks
        return [c for c in raw_chunks if not self.is_boilerplate_chunk(c)]

    def similarity_search(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query vector index with relevance gate distance & boilerplate filtering."""
        target_names = [self._get_target_collection_name(category)] if category else [self.COLLECTION_BYLAWS, self.COLLECTION_DYNAMIC]
        combined_results = []

        where_filter = {"category": category} if category else None

        for name in target_names:
            if name in self.collections and self.collections[name] is not None:
                try:
                    kwargs = {"query_texts": [query], "n_results": top_k, "include": ["documents", "metadatas", "distances"]}
                    if where_filter:
                        kwargs["where"] = where_filter
                    res = self.collections[name].query(**kwargs)

                    if res and "documents" in res and res["documents"]:
                        docs = res["documents"][0]
                        metas = res["metadatas"][0] if "metadatas" in res and res["metadatas"] else [{}] * len(docs)
                        dists = res["distances"][0] if "distances" in res and res["distances"] else [0.0] * len(docs)

                        for doc, meta, dist in zip(docs, metas, dists):
                            # Relevance Gate: Reject boilerplate chrome chunks or poor distance scores
                            if self.is_boilerplate_chunk(doc):
                                continue
                            if dist is not None and dist > self.SIMILARITY_THRESHOLD:
                                continue
                            combined_results.append({
                                "text": doc,
                                "metadata": meta,
                                "collection": name,
                                "distance": dist
                            })
                except Exception as e:
                    print(f"[ChromaDB Similarity Query Warning]: {e}")

        # Sort by best (lowest) distance score
        combined_results.sort(key=lambda x: x.get("distance", 0.0))

        # Fallback keyword match if vector search is empty
        if not combined_results:
            q_words = set(query.lower().split())
            for name in target_names:
                for doc in self._fallback_store[name]:
                    if self.is_boilerplate_chunk(doc["text"]):
                        continue
                    matches = sum(1 for w in q_words if w in doc["text"].lower())
                    if matches > 0:
                        combined_results.append({
                            "text": doc["text"],
                            "metadata": doc["metadata"],
                            "collection": name,
                            "score": matches
                        })
            combined_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return combined_results[:top_k]

    def search_relevant_context(self, query: str, category: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Alias for similarity_search to match RAG service calls."""
        results = self.similarity_search(query=query, category=category, top_k=top_k)
        formatted = []
        for r in results:
            formatted.append({
                "chunk_text": r.get("text", ""),
                "text": r.get("text", ""),
                "metadata": r.get("metadata", {}),
                "collection": r.get("collection", "")
            })
        return formatted

vector_service = DynamicVectorService()

