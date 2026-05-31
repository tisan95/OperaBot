"""Ticket management endpoints for issue escalation."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_company_id,
    get_current_user_id,
    require_admin,
)
from app.models.company import Company
from app.models.user import User as UserModel
from app.api.schemas.ticket import (
    CompanySettingsUpdate,
    TicketCreateRequest,
    TicketNoteCreate,
    TicketNoteResponse,
    TicketResponse,
    TicketStatus,
    TicketUpdateRequest,
)
from app.db.database import get_db
from app.models.ticket import Ticket, TicketNote
from app.services.llm_client import generate_answer_with_sources, SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])


def _ticket_to_response(ticket: Ticket, user_email: Optional[str] = None) -> TicketResponse:
    return TicketResponse(
        id=ticket.id,
        question=ticket.question,
        status=ticket.status,
        priority=ticket.priority,
        notes=ticket.notes,
        resolution_message=ticket.resolution_message,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        resolved_at=ticket.resolved_at,
        archived_at=ticket.archived_at,
        user_email=user_email,
    )


def _note_to_response(note: TicketNote) -> TicketNoteResponse:
    author_email = note.author.email if note.author else None
    return TicketNoteResponse(
        id=note.id,
        ticket_id=note.ticket_id,
        author_id=str(note.author_id),
        author_email=author_email,
        content=note.content,
        created_at=note.created_at,
    )


# ── POST / — crear ticket (cualquier usuario autenticado) ────────────────────

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: TicketCreateRequest,
    company_id: str = Depends(get_current_company_id),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
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
    return _ticket_to_response(ticket)


# ── GET /my — tickets del usuario autenticado ────────────────────────────────

@router.get("/my", response_model=List[TicketResponse])
async def list_my_tickets(
    include_archived: bool = False,
    user_id: str = Depends(get_current_user_id),
    company_id: str = Depends(get_current_company_id),
    db: AsyncSession = Depends(get_db),
) -> List[TicketResponse]:
    query = (
        select(Ticket)
        .where(Ticket.user_id == user_id, Ticket.company_id == company_id)
        .order_by(Ticket.created_at.desc())
    )
    if not include_archived:
        query = query.where(Ticket.archived_at.is_(None))
    result = await db.execute(query)
    tickets = result.scalars().all()
    return [_ticket_to_response(t) for t in tickets]


# ── GET / — listar todos (solo admin) ────────────────────────────────────────

@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    filter_status: Optional[TicketStatus] = None,
    include_archived: bool = False,
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> List[TicketResponse]:
    company_id = str(current_user.company_id)
    query = (
        select(Ticket)
        .where(Ticket.company_id == company_id)
        .options(selectinload(Ticket.user))
        .order_by(Ticket.created_at.desc())
    )
    if not include_archived:
        query = query.where(Ticket.archived_at.is_(None))
    if filter_status:
        query = query.where(Ticket.status == filter_status)

    result = await db.execute(query)
    tickets = result.scalars().all()
    return [_ticket_to_response(t, user_email=t.user.email if t.user else None) for t in tickets]


# ── GET /settings — retención por empresa (solo admin) ───────────────────────
# NOTE: literal routes (/settings, /archive) must be declared before parametric
#       /{ticket_id} routes so FastAPI doesn't match them as ticket IDs.

@router.get("/settings", status_code=status.HTTP_200_OK)
async def get_company_settings(
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    company_result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"ticket_retention_days": company.ticket_retention_days}


# ── PATCH /settings — actualizar retención (solo admin) ──────────────────────

@router.patch("/settings", status_code=status.HTTP_200_OK)
async def update_company_settings(
    body: CompanySettingsUpdate,
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if body.ticket_retention_days not in (7, 14, 30):
        raise HTTPException(
            status_code=400,
            detail="ticket_retention_days must be 7, 14 or 30",
        )
    company_result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.ticket_retention_days = body.ticket_retention_days
    await db.commit()
    return {"ticket_retention_days": company.ticket_retention_days}


# ── POST /archive — archivar tickets resueltos (solo admin) ──────────────────

@router.post("/archive", status_code=status.HTTP_200_OK)
async def archive_resolved_tickets(
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Archive tickets with status=resolved whose resolved_at exceeds the company
    retention window. Returns the count of archived tickets."""
    company_id = str(current_user.company_id)

    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    retention_days = getattr(company, "ticket_retention_days", 7) or 7
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    result = await db.execute(
        select(Ticket).where(
            Ticket.company_id == company_id,
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.resolved_at <= cutoff,
            Ticket.archived_at.is_(None),
        )
    )
    tickets = result.scalars().all()

    now = datetime.utcnow()
    for t in tickets:
        t.archived_at = now

    await db.commit()
    logger.info(f"[archive] Archived {len(tickets)} tickets for company={company_id}")
    return {"archived": len(tickets), "retention_days": retention_days}


# ── PATCH /{ticket_id} — actualizar ticket (solo admin) ─────────────────────

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    request: TicketUpdateRequest,
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    company_id = str(current_user.company_id)
    result = await db.execute(
        select(Ticket)
        .where(Ticket.id == ticket_id, Ticket.company_id == company_id)
        .options(selectinload(Ticket.user))
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
    if request.resolution_message is not None:
        ticket.resolution_message = request.resolution_message

    ticket.updated_at = datetime.utcnow()
    if ticket.status == TicketStatus.RESOLVED and ticket.resolved_at is None:
        ticket.resolved_at = datetime.utcnow()
    elif ticket.status != TicketStatus.RESOLVED:
        ticket.resolved_at = None

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    user_email = ticket.user.email if ticket.user else None
    return _ticket_to_response(ticket, user_email=user_email)


# ── POST /{ticket_id}/notes — añadir nota interna (solo admin) ───────────────

@router.post("/{ticket_id}/notes", response_model=TicketNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    ticket_id: int,
    request: TicketNoteCreate,
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> TicketNoteResponse:
    company_id = str(current_user.company_id)
    ticket_result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.company_id == company_id)
    )
    if not ticket_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    note = TicketNote(
        ticket_id=ticket_id,
        author_id=current_user.id,
        content=request.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return TicketNoteResponse(
        id=note.id,
        ticket_id=note.ticket_id,
        author_id=str(note.author_id),
        author_email=current_user.email,
        content=note.content,
        created_at=note.created_at,
    )


# ── GET /{ticket_id}/notes — listar notas (solo admin) ───────────────────────

@router.get("/{ticket_id}/notes", response_model=List[TicketNoteResponse])
async def list_notes(
    ticket_id: int,
    current_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> List[TicketNoteResponse]:
    company_id = str(current_user.company_id)
    ticket_result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id, Ticket.company_id == company_id)
    )
    if not ticket_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    result = await db.execute(
        select(TicketNote)
        .where(TicketNote.ticket_id == ticket_id)
        .options(selectinload(TicketNote.author))
        .order_by(TicketNote.created_at)
    )
    notes = result.scalars().all()
    return [_note_to_response(n) for n in notes]
