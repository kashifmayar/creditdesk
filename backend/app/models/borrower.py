import enum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LoanStatus(str, enum.Enum):
    ACTIVE = "active"
    OVERDUE = "overdue"
    CLOSED = "closed"
    RESTRUCTURED = "restructured"


class Borrower(Base):
    __tablename__ = "borrowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(200), nullable=True)
    cnic = Column(String(15), unique=True, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    loans = relationship("Loan", back_populates="borrower", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_number = Column(String(50), unique=True, nullable=False)
    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=False)
    principal = Column(Numeric(12, 2), nullable=False)
    installment_amount = Column(Numeric(12, 2), nullable=False)
    next_due_date = Column(Date, nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE)
    days_overdue = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    borrower = relationship("Borrower", back_populates="loans")
