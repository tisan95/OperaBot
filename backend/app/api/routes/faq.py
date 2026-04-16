"""FAQ API routes."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.dependencies import get_current_user_id
from app.api.schemas.faq import FAQCreate, FAQRead
from app.models.faq import FAQ

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get("", response_model=List[FAQRead])
async def get_faqs(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[FAQRead]:
    """Get all FAQs."""
    result = await db.execute(select(FAQ).order_by(FAQ.created_at.desc()))
    faqs = result.scalars().all()
    return faqs


@router.post("", response_model=FAQRead, status_code=status.HTTP_201_CREATED)
async def create_faq(
    request: FAQCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> FAQRead:
    """Create a new FAQ entry."""
    faq = FAQ(
        question=request.question,
        answer=request.answer,
        category=request.category,
    )
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return faq
