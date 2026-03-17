"""Document schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    doc_type: str = Field(default="sop")
    status: str = Field(default="draft")
    description: str | None = None


class DocumentUpdate(BaseModel):
    title: str | None = None
    doc_type: str | None = None
    status: str | None = None
    description: str | None = None
    current_version: int | None = None


class DocumentRead(BaseModel):
    id: str
    title: str
    doc_number: str | None = None
    doc_type: str
    status: str
    description: str | None = None
    current_version: int
    created_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentVersionCreate(BaseModel):
    version_number: int
    filename: str
    file_path: str | None = None
    change_summary: str | None = None


class DocumentVersionRead(BaseModel):
    id: str
    document_id: str
    version_number: int
    filename: str
    file_path: str | None = None
    change_summary: str | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
