from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=True)
    message_sent = Column(Text, nullable=False)
    channel = Column(String(20), default="whatsapp")
    twilio_sid = Column(String(100), nullable=True)
    status = Column(String(20), default="sent")
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    loan = relationship("Loan")
    borrower = relationship("Borrower")
    sender = relationship("User")
