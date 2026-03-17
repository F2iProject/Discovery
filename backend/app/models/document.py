"""Document Control — version-controlled protocols, methods, SOPs."""

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, TenantMixin, SoftDeleteMixin, generate_uuid


class Document(TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # sop | protocol | method | form | policy | other
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft | in_review | approved | archived
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document")
    attachments: Mapped[list["DocumentAttachment"]] = relationship(back_populates="document")


class DocumentVersion(TimestampMixin, Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    document: Mapped["Document"] = relationship(back_populates="versions")


class DocumentAttachment(TimestampMixin, Base):
    __tablename__ = "document_attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    document: Mapped["Document"] = relationship(back_populates="attachments")
