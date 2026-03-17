"""Risk schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    status: str = Field(default="draft")
    category: str | None = None
    description: str | None = None
    severity: int = Field(default=1, ge=1, le=5)
    likelihood: int = Field(default=1, ge=1, le=5)
    mitigation: str | None = None


class RiskUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    category: str | None = None
    description: str | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    likelihood: int | None = Field(default=None, ge=1, le=5)
    risk_level: str | None = None
    mitigation: str | None = None


class RiskRead(BaseModel):
    id: str
    title: str
    risk_number: str | None = None
    status: str
    category: str | None = None
    description: str | None = None
    severity: int
    likelihood: int
    risk_level: str | None = None
    mitigation: str | None = None
    created_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
