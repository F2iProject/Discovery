"""Equipment schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    location: str | None = None
    status: str = Field(default="active")
    notes: str | None = None


class EquipmentUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    location: str | None = None
    status: str | None = None
    notes: str | None = None


class EquipmentRead(BaseModel):
    id: str
    name: str
    equipment_id: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    location: str | None = None
    status: str
    notes: str | None = None
    added_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EquipmentPhotoRead(BaseModel):
    id: str
    equipment_id: str
    filename: str
    file_path: str | None = None
    description: str | None = None
    file_size: int | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
