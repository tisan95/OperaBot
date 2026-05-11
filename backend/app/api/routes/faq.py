"""FAQ API routes."""

from typing import List
import logging
import httpx
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user_id, get_current_company_id
from app.api.schemas.faq import FAQCreate, FAQRead
from app.models.faq import FAQ
from app.services.qdrant_service import qdrant_service
from qdrant_client.http.models import PointStruct

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get("", response_model=List[FAQRead])
async def get_faqs(
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id),
) -> List[FAQRead]:
    """Get all FAQs for the current company."""
    result = await db.execute(
        select(FAQ)
        .where(FAQ.company_id == company_id)
        .order_by(FAQ.created_at.desc())
    )
    faqs = result.scalars().all()
    return faqs


@router.post("", response_model=FAQRead, status_code=status.HTTP_201_CREATED)
async def create_faq(
    request: FAQCreate,
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id),
) -> FAQRead:
    """Create a new FAQ entry and store it in Qdrant."""
    try:
        logger.info(f"📝 Creating FAQ for company {company_id}: '{request.question[:50]}...'")
        
        # 1. Guardar en Base de Datos Relacional (PostgreSQL)
        faq = FAQ(
            company_id=company_id,
            question=request.question,
            answer=request.answer,
            category=request.category,
        )
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        
        # 2. Sincronizar con Qdrant (Base de datos vectorial)
        try:
            logger.info(f"🧠 Generating vector for FAQ id={faq.id}")
            combined_text = f"Pregunta: {faq.question}\nRespuesta: {faq.answer}"
            
            ollama_url = "http://localhost:11434/api/embeddings"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    ollama_url,
                    json={
                        "model": "nomic-embed-text",
                        "prompt": combined_text
                    }
                )
                vector = response.json().get("embedding")
            
            if vector:
                point_id = 2000000 + faq.id 
                
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "faq_id": faq.id,
                        "company_id": str(company_id),
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category,
                        "type": "faq"
                    }
                )
                
                qdrant_service.client.upsert(
                    collection_name="faqs",
                    points=[point]
                )
                logger.info(f"✅ FAQ id={faq.id} indexed in Qdrant successfully")
            else:
                logger.error(f"❌ Failed to get embedding for FAQ id={faq.id}")

        except Exception as q_err:
            logger.error(f"⚠️ FAQ stored in DB but Qdrant indexing failed: {q_err}")

        logger.info(f"✅ FAQ process completed for id={faq.id}")
        return faq

    except Exception as e:
        logger.error(f"❌ Error creating FAQ: {type(e).__name__}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create FAQ: {str(e)}"
        )


@router.put("/{faq_id}", response_model=FAQRead)
async def update_faq(
    faq_id: int,
    request: FAQCreate,
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id),
) -> FAQRead:
    """Update FAQ and refresh its vector in Qdrant."""
    try:
        result = await db.execute(
            select(FAQ).where(FAQ.id == faq_id, FAQ.company_id == company_id)
        )
        faq = result.scalars().first()

        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")

        faq.question = request.question
        faq.answer = request.answer
        faq.category = request.category

        await db.commit()
        await db.refresh(faq)

        try:
            combined_text = f"Pregunta: {faq.question}\nRespuesta: {faq.answer}"
            with httpx.Client(timeout=30.0) as client:
                resp = client.post("http://localhost:11434/api/embeddings", 
                                  json={"model": "nomic-embed-text", "prompt": combined_text})
                vector = resp.json().get("embedding")
            
            if vector:
                point_id = 2000000 + faq.id
                qdrant_service.client.upsert(
                    collection_name="faqs",
                    points=[PointStruct(
                        id=point_id, 
                        vector=vector, 
                        payload={
                            "faq_id": faq.id, 
                            "company_id": str(company_id),
                            "question": faq.question,
                            "answer": faq.answer,
                            "type": "faq"
                        }
                    )]
                )
                logger.info(f"✅ Qdrant updated for FAQ id={faq.id}")
        except Exception as q_err:
            logger.warning(f"⚠️ Qdrant update failed: {q_err}")

        return faq

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: int,
    db: AsyncSession = Depends(get_db),
    company_id: str = Depends(get_current_company_id),
):
    """Delete FAQ from PostgreSQL and its vector from Qdrant."""
    try:
        # 1. Fetch FAQ to ensure it exists and belongs to the company
        result = await db.execute(
            select(FAQ).where(FAQ.id == faq_id, FAQ.company_id == company_id)
        )
        faq = result.scalars().first()

        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")

        # 2. Delete from Qdrant (Sync call to avoid loop conflicts)
        try:
            point_id = 2000000 + faq_id
            logger.info(f"🗑️ Deleting Qdrant vector for FAQ id={faq_id} (point_id={point_id})")
            qdrant_service.client.delete(
                collection_name="faqs",
                points_selector=[point_id]
            )
        except Exception as q_err:
            logger.warning(f"⚠️ Failed to delete Qdrant vector for FAQ id={faq_id}: {q_err}")

        # 3. Delete from PostgreSQL
        await db.delete(faq)
        await db.commit()

        logger.info(f"✅ FAQ id={faq_id} deleted successfully from DB and Qdrant")
        return None

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Error deleting FAQ id={faq_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to delete FAQ: {str(e)}")