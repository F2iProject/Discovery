"""Deviation — document departures from established procedures."""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Deviation(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "deviations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    deviation_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    deviation_type: Mapped[str] = mapped_column(String(30), nullable=False)  # planned | unplanned
    status: Mapped[str] = mapped_column(String(30), default="open")  # open | under_review | approved | rejected | closed
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), nullable=True)
    capa_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("capas.id"), nullable=True)  # escalation link
    reported_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
