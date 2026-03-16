"""Non-Conformance — log when things don't go as planned."""

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class NonConformance(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "nonconformances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    nc_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="open")  # open | under_review | dispositioned | closed
    severity: Mapped[str] = mapped_column(String(20), default="minor")  # minor | major | critical
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # product | process | material | documentation | other
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposition: Mapped[str | None] = mapped_column(String(50), nullable=True)  # use_as_is | rework | scrap | return_to_supplier | other
    disposition_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("capas.id"), nullable=True)  # escalation link
    reported_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
