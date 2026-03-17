"""Non-Conformance schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class NonConformanceCreate(BaseModel):
    title: str = Field(..., min_length=1)
    status: str = Field(default="open")
    severity: str = Field(default="minor")
    category: str | None = None
    description: str | None = None
    disposition: str | None = None
    disposition_rationale: str | None = None
    capa_id: str | None = None


class NonConformanceUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    severity: str | None = None
    category: str | None = None
    description: str | None = None
    disposition: str | None = None
    disposition_rationale: str | None = None
    capa_id: str | None = None


class NonConformanceRead(BaseModel):
    id: str
    title: str
    nc_number: str | None = None
    status: str
    severity: str
    category: str | None = None
    description: str | None = None
    disposition: str | None = None
    disposition_rationale: str | None = None
    capa_id: str | None = None
    reported_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
