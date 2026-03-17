"""Document endpoints."""
import os
import uuid as _uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.core.config import settings
from app.database import get_db
from app.models.document import Document, DocumentAttachment, DocumentVersion
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentRead,
    DocumentVersionCreate, DocumentVersionRead,
    DocumentAttachmentRead,
)
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Document, number_prefix="DOC")

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".rtf", ".odt", ".ods", ".odp",
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".zip", ".tar", ".gz",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("", response_model=list[DocumentRead])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("", response_model=DocumentRead, status_code=201)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.create(db, payload, tenant.id, current_user.id)


@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(
    doc_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, doc_id, tenant.id)


@router.patch("/{doc_id}", response_model=DocumentRead)
def update_document(
    doc_id: str,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, doc_id, payload, tenant.id)


@router.delete("/{doc_id}", status_code=204)
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, doc_id, tenant.id)


# --- Document Versions ---

@router.get("/{doc_id}/versions", response_model=list[DocumentVersionRead])
def list_versions(
    doc_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    # Verify document exists and belongs to tenant
    service.get(db, doc_id, tenant.id)
    return db.query(DocumentVersion).filter(
        DocumentVersion.document_id == doc_id
    ).order_by(DocumentVersion.version_number).all()


@router.post("/{doc_id}/versions", response_model=DocumentVersionRead, status_code=201)
def create_version(
    doc_id: str,
    payload: DocumentVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    doc = service.get(db, doc_id, tenant.id)
    version = DocumentVersion(
        id=generate_uuid(),
        document_id=doc_id,
        version_number=payload.version_number,
        filename=payload.filename,
        file_path=payload.file_path,
        change_summary=payload.change_summary,
        uploaded_by=current_user.id,
    )
    db.add(version)
    doc.current_version = payload.version_number
    db.commit()
    db.refresh(version)
    return version


# --- File Upload / Download ---

@router.post("/{doc_id}/upload", response_model=DocumentVersionRead, status_code=201)
async def upload_file(
    doc_id: str,
    file: UploadFile = File(...),
    change_summary: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a file and create a new document version."""
    doc = service.get(db, doc_id, tenant.id)

    # Validate file extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed.",
        )

    # Read file and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    # Create upload directory: uploads/{tenant_id}/documents/{doc_id}/
    upload_dir = os.path.join(settings.UPLOAD_DIR, tenant.id, "documents", doc_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Save file with unique name to avoid collisions
    safe_filename = f"{_uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Create version record
    next_version = doc.current_version + 1
    version = DocumentVersion(
        id=generate_uuid(),
        document_id=doc_id,
        version_number=next_version,
        filename=file.filename,
        file_path=file_path,
        change_summary=change_summary or None,
        uploaded_by=current_user.id,
    )
    db.add(version)
    doc.current_version = next_version
    db.commit()
    db.refresh(version)
    return version


@router.get("/{doc_id}/versions/{version_id}/download")
def download_file(
    doc_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Download a file for a specific document version."""
    # Verify doc belongs to tenant
    service.get(db, doc_id, tenant.id)

    version = db.query(DocumentVersion).filter(
        DocumentVersion.id == version_id,
        DocumentVersion.document_id == doc_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    if not version.file_path or not os.path.isfile(version.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=version.file_path,
        filename=version.filename or os.path.basename(version.file_path),
        media_type="application/octet-stream",
    )


@router.delete("/{doc_id}/versions/{version_id}", status_code=204)
def delete_version(
    doc_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Delete a document version and its file from disk."""
    doc = service.get(db, doc_id, tenant.id)

    version = db.query(DocumentVersion).filter(
        DocumentVersion.id == version_id,
        DocumentVersion.document_id == doc_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # Remove file from disk
    if version.file_path and os.path.isfile(version.file_path):
        os.remove(version.file_path)

    db.delete(version)

    # Recalculate current_version on the document
    remaining = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == doc_id,
        DocumentVersion.id != version_id,
    ).order_by(DocumentVersion.version_number.desc()).first()
    doc.current_version = remaining.version_number if remaining else 0

    db.commit()

# --- Attachments (supporting documents, addenda, etc.) ---

@router.get("/{doc_id}/attachments", response_model=list[DocumentAttachmentRead])
def list_attachments(
    doc_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """List all attachments for a document."""
    service.get(db, doc_id, tenant.id)
    return db.query(DocumentAttachment).filter(
        DocumentAttachment.document_id == doc_id
    ).order_by(DocumentAttachment.created_at).all()


@router.post("/{doc_id}/attachments", response_model=DocumentAttachmentRead, status_code=201)
async def upload_attachment(
    doc_id: str,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a supporting document / attachment."""
    service.get(db, doc_id, tenant.id)

    # Validate extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed.",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    # Save to uploads/{tenant_id}/documents/{doc_id}/attachments/
    upload_dir = os.path.join(settings.UPLOAD_DIR, tenant.id, "documents", doc_id, "attachments")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{_uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    attachment = DocumentAttachment(
        id=generate_uuid(),
        document_id=doc_id,
        filename=file.filename,
        file_path=file_path,
        description=description or None,
        file_size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{doc_id}/attachments/{attachment_id}/download")
def download_attachment(
    doc_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Download an attachment."""
    service.get(db, doc_id, tenant.id)

    attachment = db.query(DocumentAttachment).filter(
        DocumentAttachment.id == attachment_id,
        DocumentAttachment.document_id == doc_id,
    ).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if not os.path.isfile(attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{doc_id}/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    doc_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Delete an attachment and its file from disk."""
    service.get(db, doc_id, tenant.id)

    attachment = db.query(DocumentAttachment).filter(
        DocumentAttachment.id == attachment_id,
        DocumentAttachment.document_id == doc_id,
    ).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    if os.path.isfile(attachment.file_path):
        os.remove(attachment.file_path)

    db.delete(attachment)
    db.commit()
