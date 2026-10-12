import os
import uuid
from typing import List, Dict, Any, Optional

try:
    import chromadb  # type: ignore
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

class ChromaVectorStore:
    """ChromaDB Vector Store Manager for UJ semantic embeddings."""
    def __init__(self, collection_name: str = "uj_knowledge_base"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._fallback_docs: List[Dict[str, Any]] = []

        if CHROMADB_AVAILABLE:
            try:
                persist_path = os.getenv("CHROMADB_PATH", "./chroma_db")
                self.client = chromadb.PersistentClient(path=persist_path)
                self.collection = self.client.get_or_create_collection(name=self.collection_name)
            except Exception as e:
                print(f"[ChromaDB Warning] Could not initialize PersistentClient: {e}. Using Ephemeral/InMemory client.")
                try:
                    self.client = chromadb.Client()
                    self.collection = self.client.get_or_create_collection(name=self.collection_name)
                except Exception:
                    self.client = None

    def upsert_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        if not ids:
            ids = [str(uuid.uuid4()) for _ in texts]

        if self.collection is not None:
            self.collection.upsert(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        else:
            for text, meta, doc_id in zip(texts, metadatas, ids):
                self._fallback_docs.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": meta
                })

    def delete_by_source(self, source_url: str):
        if self.collection is not None:
            try:
                self.collection.delete(where={"source_url": source_url})
            except Exception:
                pass
        else:
            self._fallback_docs = [d for d in self._fallback_docs if d.get("metadata", {}).get("source_url") != source_url]

    def query_similarity(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results_list = []
        if self.collection is not None:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    for doc, meta in zip(docs, metas):
                        results_list.append({"text": doc, "metadata": meta})
            except Exception as e:
                print(f"[ChromaDB Query Warning]: {e}")
        
        # Fallback search if vector DB returned empty or offline
        if not results_list and self._fallback_docs:
            q_words = set(query.lower().split())
            scored = []
            for doc in self._fallback_docs:
                text_lower = doc["text"].lower()
                matches = sum(1 for w in q_words if w in text_lower)
                scored.append((matches, doc))
            scored.sort(key=lambda x: x[0], reverse=True)
            results_list = [{"text": d["text"], "metadata": d["metadata"]} for m, d in scored[:top_k] if m > 0]

        return results_list

vector_store = ChromaVectorStore()
