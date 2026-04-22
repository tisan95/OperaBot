"""Qdrant vector database service for document embeddings."""

import logging
import httpx
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models as qmodels

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
            logger.error(f"Failed to ensure Qdrant collections: {e}")
            raise

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama for a text."""
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

    def search_knowledge(self, query: str, company_id: str, limit_per_collection: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Search across FAQs and documents for relevant knowledge."""
        company_id_str = str(company_id)
        
        try:
            logger.info(f"[Qdrant] Starting knowledge search for query: '{query[:50]}...'")
            
            # Request embedding synchronously
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        self.ollama_url,
                        json={
                            "model": self.embedding_model,
                            "prompt": query
                        }
                    )
                    result = response.json()
                    query_vector = result.get("embedding")
                    if not query_vector:
                        raise ValueError("No embedding returned")
            except Exception as e:
                logger.error(f"[Qdrant] Embedding request failed: {type(e).__name__}: {e}")
                return {"faqs": [], "documents": []}

            results = {"faqs": [], "documents": []}

            # Definir el filtro estricto usando los modelos oficiales de Qdrant
            strict_company_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="company_id",
                        match=qmodels.MatchValue(value=company_id_str)
                    )
                ]
            )

            # Search in FAQs collection
            try:
                faq_results = self.client.search(
                    collection_name=self.collections["faqs"],
                    query_vector=query_vector,
                    query_filter=strict_company_filter,
                    limit=limit_per_collection,
                    score_threshold=0.80  # <--- NOTA DE CORTE EXIGENTE PARA FAQS (80%)
                )
                for hit in faq_results:
                    results["faqs"].append({
                        "id": hit.id,
                        "score": hit.score,
                        "payload": hit.payload
                    })
            except Exception as e:
                logger.error(f"[Qdrant] FAQ search error: {type(e).__name__}: {e}")

            # Search in documents collection
            try:
                doc_results = self.client.search(
                    collection_name=self.collections["documents"],
                    query_vector=query_vector,
                    query_filter=strict_company_filter,
                    limit=limit_per_collection,
                    score_threshold=0.70  # <--- NOTA DE CORTE EXIGENTE PARA PDFs (70%)
                )
                for hit in doc_results:
                    results["documents"].append({
                        "id": hit.id,
                        "score": hit.score,
                        "payload": hit.payload
                    })
            except Exception as e:
                logger.error(f"[Qdrant] Document search error: {type(e).__name__}: {e}")

            logger.info(f"[Qdrant] Search completed: {len(results['faqs'])} FAQs + {len(results['documents'])} documents")
            return results

        except Exception as e:
            logger.error(f"[Qdrant] Unexpected error: {type(e).__name__}: {e}")
            return {"faqs": [], "documents": []}

    async def store_document_chunks(self, document_id: int, company_id: str,
                            chunks: List[str], metadata: Dict[str, Any]) -> int:
        """Store document chunks as vectors in Qdrant."""
        try:
            points = []
            for i, chunk in enumerate(chunks):
                vector = await self._get_embedding(chunk)
                import hashlib
                unique_str = f"{document_id}_{i}"
                unique_hash = int(hashlib.md5(unique_str.encode()).hexdigest(), 16) % (2**63 - 1)

                point = PointStruct(
                    id=unique_hash,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "company_id": str(company_id),
                        "chunk_index": i,
                        "text": chunk,
                        "filename": metadata.get("filename", ""),
                        "content_type": metadata.get("content_type", ""),
                        **metadata
                    }
                )
                points.append(point)

            self.client.upsert(
                collection_name=self.collections["documents"],
                points=points
            )
            return len(points)
        except Exception as e:
            logger.error(f"Failed to store document chunks: {e}")
            raise

    def delete_document_vectors(self, document_id: int) -> bool:
        """Delete all vectors for a document."""
        try:
            # FIX: Formato oficial de Qdrant para borrar usando filtros
            filter_selector = qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=document_id)
                        )
                    ]
                )
            )
            
            self.client.delete(
                collection_name=self.collections["documents"],
                points_selector=filter_selector
            )
            logger.info(f"[Qdrant] Successfully deleted vectors for document_id: {document_id}")
            return True
        except Exception as e:
            logger.error(f"[Qdrant] Failed to delete vectors for document_id {document_id}: {e}")
            return False


# Global instance
qdrant_service = QdrantService()