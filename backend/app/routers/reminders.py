from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.borrower import Borrower, Loan
from app.models.reminder_log import ReminderLog
from app.models.user import User
from app.schemas.reminder import (
    BulkReminderRequest,
    BulkReminderResponse,
    PaginatedReminderLogs,
    ReminderLogResponse,
    ReminderPreviewRequest,
    ReminderPreviewResponse,
    ReminderResult,
)
from app.services.twilio_service import generate_reminder_message, send_whatsapp_reminder

router = APIRouter()


def format_due_status(loan: Loan) -> str:
    if loan.days_overdue > 0:
        return f"Overdue by {loan.days_overdue} days"
    days_until = (loan.next_due_date - date.today()).days
    if days_until <= 0:
        return "Due today"
    if days_until <= 3:
        return f"Due in {days_until} days"
    return "Current"


@router.post("/preview", response_model=ReminderPreviewResponse)
async def preview_reminder(
    req: ReminderPreviewRequest,
    _: User = Depends(get_current_user),
):
    try:
        message = await generate_reminder_message(
            borrower_name=req.borrower_name,
            amount=req.amount,
            loan_number=req.loan_number,
            due_status=req.due_status,
        )
        return ReminderPreviewResponse(message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {e}")


@router.post("/send", response_model=BulkReminderResponse)
async def send_bulk_reminders(
    req: BulkReminderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    results: list[ReminderResult] = []

    for loan_id in req.loan_ids:
        result = await db.execute(
            select(Loan)
            .where(Loan.id == loan_id)
            .options(selectinload(Loan.borrower))
        )
        loan = result.scalar_one_or_none()
        if not loan or not loan.borrower:
            results.append(ReminderResult(loan_id=loan_id, status="failed", error="Loan not found"))
            continue

        borrower = loan.borrower
        due_status = format_due_status(loan)
        amount = f"{loan.installment_amount:,.0f}"

        try:
            message = await generate_reminder_message(
                borrower_name=borrower.name,
                amount=amount,
                loan_number=loan.loan_number,
                due_status=due_status,
            )
        except Exception as e:
            results.append(ReminderResult(loan_id=loan_id, status="failed", error=str(e)))
            continue

        send_result = await send_whatsapp_reminder(borrower.phone, message)
        status = send_result.get("status", "failed")

        log = ReminderLog(
            loan_id=loan.id,
            borrower_id=borrower.id,
            message_sent=message,
            channel="whatsapp",
            twilio_sid=send_result.get("sid"),
            status=status,
            sent_by=user.id,
        )
        db.add(log)

        results.append(
            ReminderResult(
                loan_id=loan_id,
                status=status,
                sid=send_result.get("sid"),
                error=send_result.get("error"),
            )
        )

    await db.flush()
    sent = len([r for r in results if r.status == "sent"])
    failed = len([r for r in results if r.status == "failed"])
    return BulkReminderResponse(
        total=len(req.loan_ids),
        sent=sent,
        failed=failed,
        results=results,
    )


@router.get("/log", response_model=PaginatedReminderLogs)
async def get_reminder_log(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    count_result = await db.execute(select(func.count()).select_from(ReminderLog))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(ReminderLog)
        .options(selectinload(ReminderLog.borrower), selectinload(ReminderLog.loan))
        .order_by(ReminderLog.sent_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = result.scalars().all()

    items = []
    for log in logs:
        item = ReminderLogResponse.model_validate(log)
        item.borrower_name = log.borrower.name if log.borrower else None
        item.loan_number = log.loan.loan_number if log.loan else None
        items.append(item)

    return PaginatedReminderLogs(items=items, total=total, page=page, page_size=page_size)
