"""Qdrant vector database service for document embeddings."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for managing vector embeddings in Qdrant using Ollama."""

    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333,
            timeout=30.0
        )
        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.embedding_model = "nomic-embed-text"
        self.collections = {
            "documents": "documents",  # PDF documents
            "faqs": "faqs"  # FAQ entries
        }

        # Ensure collections exist
        self._ensure_collections()

    def _ensure_collections(self):
        """Create collections if they don't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            for collection_name in self.collections.values():
                if collection_name not in collection_names:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=768,  # nomic-embed-text produces 768-dimensional vectors
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created Qdrant collection: {collection_name}")
                else:
                    logger.info(f"Qdrant collection already exists: {collection_name}")
        except Exception as e:
            # Non-fatal: Qdrant may not be running (e.g. in tests or local dev without vector DB).
            # RAG calls will return empty results and fall back gracefully.
            logger.warning(f"[Qdrant] Collections not ready (service may be offline): {e}")

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama for a text.

        Args:
            text: Text to embed

        Returns:
            Vector embedding as list of floats
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )
                result = response.json()
                embedding = result.get("embedding")
                if not embedding:
                    raise ValueError("No embedding returned from Ollama")
                return embedding
        except Exception as e:
            logger.error(f"Failed to get embedding from Ollama: {e}")
            raise

    async def search_knowledge(self, query: str, company_id: str, limit_per_collection: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Search across FAQs and documents for relevant knowledge.

        Args:
            query: Search query text
            company_id: Company ID for filtering
            limit_per_collection: Maximum results per collection

        Returns:
            Dict with 'faqs' and 'documents' keys containing search results
        """
        try:
            logger.info(f"[Qdrant] Starting knowledge search for query: '{query[:50]}...'")
            
            # Get embedding with timeout
            try:
                logger.info(f"[Qdrant] Requesting embedding from Ollama...")
                query_vector = await self._get_embedding(query)
                logger.info(f"[Qdrant] Embedding received: {len(query_vector)} dimensions")
            except Exception as e:
                logger.error(f"[Qdrant] Embedding request failed: {type(e).__name__}: {e}")
                return {"faqs": [], "documents": []}

            results = {"faqs": [], "documents": []}

            # Search in FAQs collection
            try:
                logger.info(f"[Qdrant] Searching FAQs collection...")
                faq_results = self.client.search(
                    collection_name=self.collections["faqs"],
                    query_vector=query_vector,
                    query_filter={
                        "must": [{"key": "company_id", "match": {"value": company_id}}]
                    },
                    limit=limit_per_collection
                )
                for hit in faq_results:
                    results["faqs"].append({
                        "id": hit.id,
                        "score": hit.score,
                        "payload": hit.payload
                    })
                logger.info(f"[Qdrant] FAQ search returned {len(results['faqs'])} results")
            except Exception as e:
                logger.error(f"[Qdrant] FAQ search error: {type(e).__name__}: {e}", exc_info=True)

            # Search in documents collection
            try:
                logger.info(f"[Qdrant] Searching documents collection...")
                doc_results = self.client.search(
                    collection_name=self.collections["documents"],
                    query_vector=query_vector,
                    query_filter={
                        "must": [{"key": "company_id", "match": {"value": company_id}}]
                    },
                    limit=limit_per_collection
                )
                for hit in doc_results:
                    results["documents"].append({
                        "id": hit.id,
                        "score": hit.score,
                        "payload": hit.payload
                    })
                logger.info(f"[Qdrant] Document search returned {len(results['documents'])} results")
            except Exception as e:
                logger.error(f"[Qdrant] Document search error: {type(e).__name__}: {e}", exc_info=True)

            logger.info(f"[Qdrant] Knowledge search completed: {len(results['faqs'])} FAQs + {len(results['documents'])} documents")
            return results

        except Exception as e:
            logger.error(f"[Qdrant] Unexpected error in knowledge search: {type(e).__name__}: {e}", exc_info=True)
            return {"faqs": [], "documents": []}

    async def store_document_chunks(self, document_id: int, company_id: str,
                            chunks: List[str], metadata: Dict[str, Any]) -> int:
        """Store document chunks as vectors in Qdrant.

        Args:
            document_id: Database document ID
            company_id: Company ID
            chunks: List of text chunks
            metadata: Additional metadata (filename, etc.)

        Returns:
            Number of vectors stored
        """
        try:
            points = []

            for i, chunk in enumerate(chunks):
                # Get embedding from Ollama
                vector = await self._get_embedding(chunk)

                # Create unique integer ID for Qdrant (hash of doc_id + chunk index)
                # Qdrant requires either unsigned integer or UUID as point ID
                import hashlib
                unique_str = f"{document_id}_{i}"
                unique_hash = int(hashlib.md5(unique_str.encode()).hexdigest(), 16) % (2**63 - 1)

                # Create point with metadata
                point = PointStruct(
                    id=unique_hash,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "company_id": company_id,
                        "chunk_index": i,
                        "text": chunk,
                        "filename": metadata.get("filename", ""),
                        "content_type": metadata.get("content_type", ""),
                        **metadata
                    }
                )
                points.append(point)

            # Upsert points to Qdrant
            self.client.upsert(
                collection_name=self.collections["documents"],
                points=points
            )

            logger.info(f"Stored {len(points)} vectors for document {document_id}")
            return len(points)

        except Exception as e:
            logger.error(f"Failed to store document chunks in Qdrant: {e}")
            raise

    def delete_document_vectors(self, document_id: int) -> bool:
        """Delete all vectors for a document.

        Args:
            document_id: Database document ID

        Returns:
            True if successful
        """
        try:
            # Delete points with matching document_id
            self.client.delete(
                collection_name=self.collections["documents"],
                points_selector={
                    "filter": {
                        "must": [
                            {"key": "document_id", "match": {"value": document_id}}
                        ]
                    }
                }
            )

            logger.info(f"Deleted vectors for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document vectors: {e}")
            return False


# Global instance
qdrant_service = QdrantService()
