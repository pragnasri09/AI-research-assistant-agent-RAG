import os
import chromadb
import logging
from typing import List, Dict, Any
from app.rag.embeddings import get_embedding_function
from app.config import settings

logger = logging.getLogger(__name__)

class ResearchVectorStore:
    def __init__(self, session_id: str):
        self.session_id = session_id
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.embedding_fn = get_embedding_function()
        # Clean collection name safe for ChromaDB
        safe_name = f"session_{session_id.replace('-', '_')}"
        self.collection = self.client.get_or_create_collection(
            name=safe_name,
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        ids = [c["chunk_id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [{
            "source_id": c["source_id"],
            "title": c["title"],
            "url": c["url"],
            "domain": c["domain"]
        } for c in chunks]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Added {len(chunks)} chunks to ChromaDB vector store for session {self.session_id}")

    def query(self, query_text: str, top_k: int = settings.RETRIEVAL_TOP_K) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        retrieved = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            
            for d, m, i, dist in zip(docs, metas, ids, distances):
                retrieved.append({
                    "chunk_id": i,
                    "content": d,
                    "source_id": m.get("source_id"),
                    "title": m.get("title", ""),
                    "url": m.get("url", ""),
                    "domain": m.get("domain", ""),
                    "distance": dist
                })
        return retrieved

    def delete_collection(self):
        try:
            safe_name = f"session_{self.session_id.replace('-', '_')}"
            self.client.delete_collection(name=safe_name)
        except Exception:
            pass
