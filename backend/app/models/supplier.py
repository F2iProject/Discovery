"""Supplier — where you get your stuff."""

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Supplier(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    mpn: Mapped[str | None] = mapped_column(String(255), nullable=True)  # manufacturer part number
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    supplies: Mapped[str | None] = mapped_column(Text, nullable=True)  # what they provide
    qualification_status: Mapped[str] = mapped_column(String(30), default="pending")  # pending | approved | conditional | disqualified
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    documents: Mapped[list["SupplierDocument"]] = relationship(back_populates="supplier")


class SupplierDocument(TimestampMixin, Base):
    __tablename__ = "supplier_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    supplier: Mapped["Supplier"] = relationship(back_populates="documents")
