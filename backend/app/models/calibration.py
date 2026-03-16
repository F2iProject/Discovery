"""Calibration — track calibration schedules and results."""

from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, generate_uuid


class CalibrationRecord(TimestampMixin, TenantMixin, Base):
    __tablename__ = "calibration_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    equipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("equipment.id"), nullable=False)
    calibration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)  # days between calibrations
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # pass | fail | adjusted
    method: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certificate_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
