"""Training schemas."""
from datetime import date, datetime
from pydantic import BaseModel, Field


class TrainingCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None = None
    url: str | None = None
    status: str = Field(default="draft")
    document_id: str | None = None


class TrainingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    url: str | None = None
    status: str | None = None
    document_id: str | None = None


class TrainingRead(BaseModel):
    id: str
    title: str
    description: str | None = None
    url: str | None = None
    status: str
    document_id: str | None = None
    created_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrainingAssignmentCreate(BaseModel):
    user_id: str
    status: str = Field(default="assigned")
    due_date: date | None = None


class TrainingAssignmentUpdate(BaseModel):
    status: str | None = None
    due_date: date | None = None


class TrainingAssignmentRead(BaseModel):
    id: str
    training_id: str
    user_id: str
    status: str
    completed_at: datetime | None = None
    due_date: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TrainingMaterialRead(BaseModel):
    id: str
    training_id: str
    filename: str
    file_path: str | None = None
    description: str | None = None
    file_size: int | None = None
    uploaded_by: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
