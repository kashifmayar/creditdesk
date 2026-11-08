from datetime import datetime

from pydantic import BaseModel, Field


class ReminderPreviewRequest(BaseModel):
    borrower_name: str
    amount: str
    loan_number: str
    due_status: str


class ReminderPreviewResponse(BaseModel):
    message: str


class BulkReminderRequest(BaseModel):
    loan_ids: list[int] = Field(..., min_length=1)


class ReminderResult(BaseModel):
    loan_id: int
    status: str
    sid: str | None = None
    error: str | None = None


class BulkReminderResponse(BaseModel):
    total: int
    sent: int
    failed: int
    results: list[ReminderResult]


class ReminderLogResponse(BaseModel):
    id: int
    loan_id: int | None
    borrower_id: int | None
    message_sent: str
    channel: str
    twilio_sid: str | None
    status: str
    sent_at: datetime | None
    borrower_name: str | None = None
    loan_number: str | None = None

    model_config = {"from_attributes": True}


class PaginatedReminderLogs(BaseModel):
    items: list[ReminderLogResponse]
    total: int
    page: int
    page_size: int


class ReminderListUploadResponse(BaseModel):
    filename: str
    rows_read: int
    borrowers_created: int
    loans_created: int
    message: str
