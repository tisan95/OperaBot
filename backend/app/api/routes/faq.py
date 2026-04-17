"""FAQ API routes."""

from typing import List
import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user_id, get_current_company_id
from app.api.schemas.faq import FAQCreate, FAQRead
from app.models.faq import FAQ

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
    """Create a new FAQ entry for the current company."""
    try:
        logger.info(f"📝 Creating FAQ for company {company_id}: '{request.question[:50]}...'")
        
        faq = FAQ(
            company_id=company_id,
            question=request.question,
            answer=request.answer,
            category=request.category,
        )
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        
        logger.info(f"✅ FAQ created successfully with id={faq.id}")
        return faq
    except Exception as e:
        logger.error(f"❌ Error creating FAQ: {type(e).__name__}: {e}", exc_info=True)
        
        # Rollback transaction to avoid leaving it in a failed state
        try:
            await db.rollback()
            logger.info("✅ Database transaction rolled back")
        except Exception as rollback_err:
            logger.warning(f"⚠️ Failed to rollback transaction: {rollback_err}")
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create FAQ: {str(e)}"
        )
