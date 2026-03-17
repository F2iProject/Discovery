"""Complaint — customer feedback intake and tracking."""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Complaint(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    complaint_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open | under_review | closed
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # customer name or identifier
    product: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    investigation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("capas.id"), nullable=True)  # escalation link
    reported_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
