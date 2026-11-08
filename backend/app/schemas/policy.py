from pydantic import BaseModel, Field


class PolicyAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class PolicyAskResponse(BaseModel):
    answer: str
    context_used: str


class PolicyUploadResponse(BaseModel):
    chunks_ingested: int
    status: str
    filename: str | None = None
    pages: int | None = None
    sha256: str | None = None


class PolicyStatusResponse(BaseModel):
    loaded: bool
    filename: str | None = None
    pages: int | None = None
    chunks_ingested: int | None = None
    ingested_at: str | None = None
