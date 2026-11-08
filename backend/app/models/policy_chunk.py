from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base
from app.config import settings


class PolicyChunk(Base):
    __tablename__ = "policy_chunks"

    id = Column(Integer, primary_key=True, index=True)
    policy_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    section_title = Column(String(300), nullable=True)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
