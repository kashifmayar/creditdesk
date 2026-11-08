from sqlalchemy import Boolean, Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.sql import func

from app.database import Base


class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(300), nullable=False)
    sha256 = Column(String(64), nullable=True)
    file_data = Column(LargeBinary, nullable=False)
    pages = Column(Integer, nullable=False, default=0)
    chunk_count = Column(Integer, nullable=False, default=0)
    embedded_count = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
