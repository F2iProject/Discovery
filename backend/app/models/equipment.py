"""Equipment — registry of lab instruments and devices."""

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Equipment(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    equipment_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # asset tag / lab ID
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # analytical | imaging | prep | computing | other
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active")  # active | maintenance | retired | out_of_service
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    photos: Mapped[list["EquipmentPhoto"]] = relationship(back_populates="equipment")


class EquipmentPhoto(TimestampMixin, Base):
    __tablename__ = "equipment_photos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    equipment_id: Mapped[str] = mapped_column(String(36), ForeignKey("equipment.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    equipment: Mapped["Equipment"] = relationship(back_populates="photos")
