from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class LoanBase(BaseModel):
    loan_number: str
    principal: Decimal
    installment_amount: Decimal
    next_due_date: date
    status: str = "active"
    days_overdue: int = 0


class LoanResponse(LoanBase):
    id: int
    borrower_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class BorrowerCreate(BaseModel):
    name: str = Field(..., max_length=200)
    phone: str = Field(..., max_length=20)
    email: EmailStr | None = None
    cnic: str = Field(..., max_length=15)


class BorrowerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class BorrowerResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    cnic: str
    created_at: datetime | None = None
    loans: list[LoanResponse] = []

    model_config = {"from_attributes": True}


class DueBorrowerResponse(BaseModel):
    loan_id: int
    borrower_id: int
    name: str
    phone: str
    loan_number: str
    installment_amount: Decimal
    next_due_date: date
    due_status: str
    days_overdue: int


class PaginatedBorrowers(BaseModel):
    items: list[BorrowerResponse]
    total: int
    page: int
    page_size: int
