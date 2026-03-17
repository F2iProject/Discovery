"""Deviation schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class DeviationCreate(BaseModel):
    title: str = Field(..., min_length=1)
    deviation_type: str = Field(default="unplanned")
    status: str = Field(default="open")
    description: str | None = None
    justification: str | None = None
    resolution: str | None = None
    affected_document_id: str | None = None
    capa_id: str | None = None


class DeviationUpdate(BaseModel):
    title: str | None = None
    deviation_type: str | None = None
    status: str | None = None
    description: str | None = None
    justification: str | None = None
    resolution: str | None = None
    affected_document_id: str | None = None
    capa_id: str | None = None


class DeviationRead(BaseModel):
    id: str
    title: str
    deviation_number: str | None = None
    deviation_type: str
    status: str
    description: str | None = None
    justification: str | None = None
    resolution: str | None = None
    affected_document_id: str | None = None
    capa_id: str | None = None
    reported_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
