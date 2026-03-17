"""Change Control schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class ChangeControlCreate(BaseModel):
    title: str = Field(..., min_length=1)
    change_type: str = Field(default="process")
    status: str = Field(default="draft")
    description: str | None = None
    justification: str | None = None
    impact_assessment: str | None = None
    document_id: str | None = None


class ChangeControlUpdate(BaseModel):
    title: str | None = None
    change_type: str | None = None
    status: str | None = None
    description: str | None = None
    justification: str | None = None
    impact_assessment: str | None = None
    document_id: str | None = None


class ChangeControlRead(BaseModel):
    id: str
    title: str
    change_number: str | None = None
    status: str
    change_type: str
    description: str | None = None
    justification: str | None = None
    impact_assessment: str | None = None
    requested_by: str | None = None
    document_id: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
