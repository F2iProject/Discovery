"""CAPA — Corrective and Preventive Action tracking."""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class CAPA(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "capas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    capa_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    capa_type: Mapped[str] = mapped_column(String(20), nullable=False)  # corrective | preventive
    status: Mapped[str] = mapped_column(String(30), default="open")  # open | investigation | action_defined | implemented | closed
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low | medium | high | critical
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # nc | deviation | complaint | audit | other
    source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # links to originating record
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    actions: Mapped[list["CAPAAction"]] = relationship(back_populates="capa")


class CAPAAction(TimestampMixin, Base):
    __tablename__ = "capa_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    capa_id: Mapped[str] = mapped_column(String(36), ForeignKey("capas.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String(20), nullable=False)  # correction | corrective | preventive
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | in_progress | completed
    assigned_to: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    capa: Mapped["CAPA"] = relationship(back_populates="actions")
