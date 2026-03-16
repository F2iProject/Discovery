"""Risk Register — identify and assess risks."""

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Risk(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    risk_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft | active | mitigated | closed
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # safety | process | design | regulatory | other
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    likelihood: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low | medium | high
    mitigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
