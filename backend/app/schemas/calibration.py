"""Calibration schemas."""
from datetime import date, datetime
from pydantic import BaseModel, Field


class CalibrationCreate(BaseModel):
    equipment_id: str
    calibration_date: date
    next_due: date | None = None
    interval_days: int | None = None
    result: str = Field(default="pass")
    method: str | None = None
    certificate_ref: str | None = None
    notes: str | None = None


class CalibrationUpdate(BaseModel):
    calibration_date: date | None = None
    next_due: date | None = None
    interval_days: int | None = None
    result: str | None = None
    method: str | None = None
    certificate_ref: str | None = None
    notes: str | None = None


class CalibrationRead(BaseModel):
    id: str
    equipment_id: str
    calibration_date: date
    next_due: date | None = None
    interval_days: int | None = None
    result: str
    method: str | None = None
    certificate_ref: str | None = None
    notes: str | None = None
    performed_by: str | None = None
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
