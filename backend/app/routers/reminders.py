from datetime import date
from decimal import Decimal
from io import BytesIO
import re

import fitz
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from openpyxl import load_workbook
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.borrower import Borrower, Loan, LoanStatus
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
    ReminderListUploadResponse,
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


def _first_of_current_month() -> date:
    today = date.today()
    return date(today.year, today.month, 1)


def _sanitize_phone(phone: str) -> str:
    clean = re.sub(r"[^\d+]", "", phone or "")
    return clean


def _to_decimal(value: str | int | float | Decimal | None) -> Decimal:
    if value is None:
        return Decimal("0")
    text = str(value).replace(",", "").strip()
    if not text:
        return Decimal("0")
    return Decimal(text)


def _parse_pdf_rows(file_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    lines: list[str] = []
    for page in doc:
        text = page.get_text()
        lines.extend([ln.strip() for ln in text.splitlines() if ln.strip()])
    doc.close()

    rows: list[dict] = []
    for line in lines:
        if not any(sep in line for sep in [",", "|", "\t"]):
            continue
        parts = [p.strip() for p in re.split(r"[,\|\t]+", line) if p.strip()]
        if len(parts) < 4:
            continue
        # Expected order: name, phone, loan_number, installment_amount[, cnic, email, principal]
        rows.append(
            {
                "name": parts[0],
                "phone": parts[1],
                "loan_number": parts[2],
                "installment_amount": parts[3],
                "cnic": parts[4] if len(parts) > 4 else None,
                "email": parts[5] if len(parts) > 5 else None,
                "principal": parts[6] if len(parts) > 6 else None,
            }
        )
    return rows


def _parse_excel_rows(file_bytes: bytes) -> list[dict]:
    wb = load_workbook(filename=BytesIO(file_bytes), data_only=True)
    ws = wb.active
    rows: list[dict] = []
    header = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]
    idx = {name: i for i, name in enumerate(header)}

    def get_value(row, key, fallback_index):
        if key in idx:
            val = row[idx[key]].value
            return "" if val is None else str(val).strip()
        if fallback_index < len(row):
            val = row[fallback_index].value
            return "" if val is None else str(val).strip()
        return ""

    for r in ws.iter_rows(min_row=2):
        name = get_value(r, "name", 0)
        phone = get_value(r, "phone", 1)
        loan_number = get_value(r, "loan_number", 2)
        installment_amount = get_value(r, "installment_amount", 3)
        if not (name and phone and loan_number and installment_amount):
            continue
        rows.append(
            {
                "name": name,
                "phone": phone,
                "loan_number": loan_number,
                "installment_amount": installment_amount,
                "cnic": get_value(r, "cnic", 4) or None,
                "email": get_value(r, "email", 5) or None,
                "principal": get_value(r, "principal", 6) or None,
            }
        )
    return rows


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


@router.post("/upload-list", response_model=ReminderListUploadResponse)
async def upload_reminder_list(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")
    ext = file.filename.lower().split(".")[-1]
    if ext not in {"pdf", "xlsx", "xls"}:
        raise HTTPException(status_code=400, detail="Upload PDF or Excel file (.pdf, .xlsx, .xls)")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    rows = _parse_pdf_rows(file_bytes) if ext == "pdf" else _parse_excel_rows(file_bytes)
    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No valid rows found. Expected columns: name, phone, loan_number, installment_amount",
        )

    due_date = _first_of_current_month()
    today = date.today()
    overdue_days = max((today - due_date).days, 0)
    loan_status = LoanStatus.OVERDUE if overdue_days > 0 else LoanStatus.ACTIVE

    borrowers_created = 0
    loans_created = 0

    for row in rows:
        result = await db.execute(
            select(Borrower).where(
                Borrower.phone == _sanitize_phone(row["phone"]),
                Borrower.is_deleted.is_(False),
            )
        )
        borrower = result.scalar_one_or_none()
        if borrower is None:
            cnic = row["cnic"] or f"AUTO-{re.sub(r'[^0-9]', '', row['phone'])[:10]}-{len(row['name'])}"
            borrower = Borrower(
                name=row["name"],
                phone=_sanitize_phone(row["phone"]),
                email=row["email"],
                cnic=cnic[:15],
            )
            db.add(borrower)
            await db.flush()
            borrowers_created += 1

        existing_loan = await db.execute(select(Loan).where(Loan.loan_number == row["loan_number"]))
        if existing_loan.scalar_one_or_none():
            continue

        installment = _to_decimal(row["installment_amount"])
        principal = _to_decimal(row["principal"]) if row["principal"] else installment * 10
        db.add(
            Loan(
                loan_number=row["loan_number"],
                borrower_id=borrower.id,
                principal=principal,
                installment_amount=installment,
                next_due_date=due_date,
                status=loan_status,
                days_overdue=overdue_days,
            )
        )
        loans_created += 1

    await db.flush()
    return ReminderListUploadResponse(
        filename=file.filename,
        rows_read=len(rows),
        borrowers_created=borrowers_created,
        loans_created=loans_created,
        message=(
            "Reminder list uploaded. Installment due date set to the 1st of current month for all imported loans."
        ),
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
