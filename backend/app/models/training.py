"""Training — track who needs to learn what."""

from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Training(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "trainings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)  # external link (video, LMS, web resource)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft | active | retired
    document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("documents.id"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    assignments: Mapped[list["TrainingAssignment"]] = relationship(back_populates="training")
    materials: Mapped[list["TrainingMaterial"]] = relationship(back_populates="training")


class TrainingAssignment(TimestampMixin, Base):
    __tablename__ = "training_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    training_id: Mapped[str] = mapped_column(String(36), ForeignKey("trainings.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="assigned")  # assigned | in_progress | completed
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    training: Mapped["Training"] = relationship(back_populates="assignments")


class TrainingMaterial(TimestampMixin, Base):
    __tablename__ = "training_materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    training_id: Mapped[str] = mapped_column(String(36), ForeignKey("trainings.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    training: Mapped["Training"] = relationship(back_populates="materials")
