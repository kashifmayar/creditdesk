from pydantic import BaseModel, Field


class PolicyAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class PolicyAskResponse(BaseModel):
    answer: str
    context_used: str


class PolicyUploadResponse(BaseModel):
    chunks_ingested: int
    status: str
