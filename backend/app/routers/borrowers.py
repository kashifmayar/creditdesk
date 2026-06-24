from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.borrower import Borrower, Loan, LoanStatus
from app.models.reminder_log import ReminderLog
from app.models.user import User
from app.schemas.borrower import (
    BorrowerCreate,
    BorrowerResponse,
    BorrowerUpdate,
    DueBorrowerResponse,
    PaginatedBorrowers,
)

router = APIRouter()


def compute_due_status(next_due: date, days_overdue: int) -> str:
    if days_overdue > 0:
        return "overdue"
    days_until = (next_due - date.today()).days
    if days_until <= 0:
        return "due_today"
    if days_until <= 3:
        return "due_soon"
    return "current"


@router.get("/due", response_model=list[DueBorrowerResponse])
async def get_due_borrowers(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Loan, Borrower)
        .join(Borrower, Loan.borrower_id == Borrower.id)
        .where(
            Borrower.is_deleted.is_(False),
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
        )
        .order_by(Loan.next_due_date)
    )
    rows = result.all()
    due_list = []
    for loan, borrower in rows:
        due_status = compute_due_status(loan.next_due_date, loan.days_overdue)
        if due_status in ("overdue", "due_today", "due_soon"):
            due_list.append(
                DueBorrowerResponse(
                    loan_id=loan.id,
                    borrower_id=borrower.id,
                    name=borrower.name,
                    phone=borrower.phone,
                    loan_number=loan.loan_number,
                    installment_amount=loan.installment_amount,
                    next_due_date=loan.next_due_date,
                    due_status=due_status,
                    days_overdue=loan.days_overdue,
                )
            )
    return due_list


@router.get("", response_model=PaginatedBorrowers)
async def list_borrowers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    count_result = await db.execute(
        select(func.count()).select_from(Borrower).where(Borrower.is_deleted.is_(False))
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Borrower)
        .where(Borrower.is_deleted.is_(False))
        .options(selectinload(Borrower.loans))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(Borrower.id)
    )
    borrowers = result.scalars().all()
    return PaginatedBorrowers(
        items=[BorrowerResponse.model_validate(b) for b in borrowers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=BorrowerResponse, status_code=201)
async def create_borrower(
    req: BorrowerCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    existing = await db.execute(select(Borrower).where(Borrower.cnic == req.cnic))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="CNIC already registered")

    borrower = Borrower(**req.model_dump())
    db.add(borrower)
    await db.flush()
    await db.refresh(borrower, ["loans"])
    return BorrowerResponse.model_validate(borrower)


@router.get("/{borrower_id}", response_model=BorrowerResponse)
async def get_borrower(
    borrower_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Borrower)
        .where(Borrower.id == borrower_id, Borrower.is_deleted.is_(False))
        .options(selectinload(Borrower.loans))
    )
    borrower = result.scalar_one_or_none()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return BorrowerResponse.model_validate(borrower)


@router.put("/{borrower_id}", response_model=BorrowerResponse)
async def update_borrower(
    borrower_id: int,
    req: BorrowerUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Borrower)
        .where(Borrower.id == borrower_id, Borrower.is_deleted.is_(False))
        .options(selectinload(Borrower.loans))
    )
    borrower = result.scalar_one_or_none()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(borrower, field, value)
    await db.flush()
    return BorrowerResponse.model_validate(borrower)


@router.delete("/{borrower_id}", status_code=204)
async def delete_borrower(
    borrower_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Borrower).where(Borrower.id == borrower_id, Borrower.is_deleted.is_(False))
    )
    borrower = result.scalar_one_or_none()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    borrower.is_deleted = True


@router.get("/metrics/summary")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    today = date.today()
    active_result = await db.execute(
        select(func.count()).select_from(Loan).where(Loan.status == LoanStatus.ACTIVE)
    )
    overdue_result = await db.execute(
        select(func.count()).select_from(Loan).where(Loan.status == LoanStatus.OVERDUE)
    )
    due_today_result = await db.execute(
        select(func.count())
        .select_from(Loan)
        .where(Loan.next_due_date == today, Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]))
    )
    reminders_today_result = await db.execute(
        select(func.count())
        .select_from(ReminderLog)
        .where(
            func.date(ReminderLog.sent_at) == today,
            ReminderLog.status == "sent",
        )
    )
    return {
        "active_loans": active_result.scalar() or 0,
        "due_today": due_today_result.scalar() or 0,
        "overdue": overdue_result.scalar() or 0,
        "reminders_sent_today": reminders_today_result.scalar() or 0,
    }
