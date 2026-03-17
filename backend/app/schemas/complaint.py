"""Complaint schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=1)
    status: str = Field(default="open")
    source: str | None = None
    product: str | None = None
    lot_number: str | None = None
    description: str | None = None
    investigation_notes: str | None = None
    capa_id: str | None = None


class ComplaintUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    source: str | None = None
    product: str | None = None
    lot_number: str | None = None
    description: str | None = None
    investigation_notes: str | None = None
    capa_id: str | None = None


class ComplaintRead(BaseModel):
    id: str
    title: str
    complaint_number: str | None = None
    status: str
    source: str | None = None
    product: str | None = None
    lot_number: str | None = None
    description: str | None = None
    investigation_notes: str | None = None
    capa_id: str | None = None
    reported_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
