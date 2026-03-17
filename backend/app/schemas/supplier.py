"""Supplier schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1)
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str = Field(default="pending")
    notes: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str | None = None
    notes: str | None = None


class SupplierRead(BaseModel):
    id: str
    name: str
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str
    notes: str | None = None
    added_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
