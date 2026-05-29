"""Ticket management endpoints for issue escalation."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_company_id, get_current_user_id
from app.api.schemas.ticket import (
    TicketCreateRequest,
    TicketResponse,
    TicketUpdateRequest,
    TicketStatus,
)
from app.db.database import get_db
from app.models.ticket import Ticket
from app.services.llm_client import generate_answer_with_sources, SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: TicketCreateRequest,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Create a ticket when the chat confidence threshold is not met."""
    bot_response = await generate_answer_with_sources(request.question, company_id)
    if bot_response.get("confidence", 0.0) >= SIMILARITY_THRESHOLD and bot_response.get("sources"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat confidence is sufficient; no ticket was created.",
        )

    ticket = Ticket(
        company_id=company_id,
        user_id=user_id,
        question=request.question,
        status=TicketStatus.OPEN,
        priority=request.priority,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return TicketResponse(
        id=ticket.id,
        question=ticket.question,
        status=ticket.status,
        priority=ticket.priority,
        notes=ticket.notes,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
    )


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[TicketStatus] = None,
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> List[TicketResponse]:
    """List tickets for the current company, optional status filter."""
    query = select(Ticket).where(Ticket.company_id == company_id)
    if status:
        query = query.where(Ticket.status == status)

    result = await db.execute(query)
    tickets = result.scalars().all()

    return [
        TicketResponse(
            id=ticket.id,
            question=ticket.question,
            status=ticket.status,
            priority=ticket.priority,
            notes=ticket.notes,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            resolved_at=ticket.resolved_at,
        )
        for ticket in tickets
    ]


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    request: TicketUpdateRequest,
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Update ticket status, priority, or notes."""
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.company_id == company_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if request.status is not None:
        ticket.status = request.status
    if request.priority is not None:
        ticket.priority = request.priority
    if request.notes is not None:
        ticket.notes = request.notes

    ticket.updated_at = datetime.utcnow()
    if ticket.status == TicketStatus.RESOLVED and ticket.resolved_at is None:
        ticket.resolved_at = datetime.utcnow()
    elif ticket.status != TicketStatus.RESOLVED:
        ticket.resolved_at = None

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return TicketResponse(
        id=ticket.id,
        question=ticket.question,
        status=ticket.status,
        priority=ticket.priority,
        notes=ticket.notes,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
    )
