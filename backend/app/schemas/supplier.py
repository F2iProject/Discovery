"""Supplier schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1)
    mpn: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str = Field(default="pending")
    notes: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    mpn: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str | None = None
    notes: str | None = None


class SupplierRead(BaseModel):
    id: str
    name: str
    mpn: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    supplies: str | None = None
    qualification_status: str
    notes: str | None = None
    added_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierDocumentRead(BaseModel):
    id: str
    supplier_id: str
    filename: str
    file_path: str | None = None
    description: str | None = None
    file_size: int | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
