"""Training — track who needs to learn what."""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Training(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "trainings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft | active | retired
    document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    assignments: Mapped[list["TrainingAssignment"]] = relationship(back_populates="training")


class TrainingAssignment(TimestampMixin, Base):
    __tablename__ = "training_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    training_id: Mapped[str] = mapped_column(String(36), ForeignKey("trainings.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="assigned")  # assigned | in_progress | completed
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    training: Mapped["Training"] = relationship(back_populates="assignments")
