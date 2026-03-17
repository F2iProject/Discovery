"""CAPA schemas."""
from datetime import date, datetime
from pydantic import BaseModel, Field


class CAPACreate(BaseModel):
    title: str = Field(..., min_length=1)
    capa_type: str = Field(default="corrective")
    status: str = Field(default="open")
    priority: str = Field(default="medium")
    description: str | None = None
    root_cause: str | None = None
    source: str | None = None
    source_id: str | None = None
    target_date: date | None = None


class CAPAUpdate(BaseModel):
    title: str | None = None
    capa_type: str | None = None
    status: str | None = None
    priority: str | None = None
    description: str | None = None
    root_cause: str | None = None
    source: str | None = None
    source_id: str | None = None
    target_date: date | None = None
    closed_date: date | None = None


class CAPARead(BaseModel):
    id: str
    title: str
    capa_number: str | None = None
    capa_type: str
    status: str
    priority: str
    description: str | None = None
    root_cause: str | None = None
    source: str | None = None
    source_id: str | None = None
    target_date: date | None = None
    closed_date: date | None = None
    created_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CAPAActionCreate(BaseModel):
    description: str = Field(..., min_length=1)
    action_type: str = Field(default="corrective")
    status: str = Field(default="open")
    assigned_to: str | None = None


class CAPAActionUpdate(BaseModel):
    description: str | None = None
    action_type: str | None = None
    status: str | None = None
    assigned_to: str | None = None


class CAPAActionRead(BaseModel):
    id: str
    capa_id: str
    description: str
    action_type: str
    status: str
    assigned_to: str | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
