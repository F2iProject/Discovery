"""Supplier endpoints — CRUD + vendor documents."""

import os
import uuid as _uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.supplier import Supplier, SupplierDocument
from app.models.mixins import generate_uuid
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierRead, SupplierDocumentRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Supplier, number_prefix=None)

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".rtf", ".odt", ".ods", ".odp",
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".zip", ".tar", ".gz",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("", response_model=list[SupplierRead])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("", response_model=SupplierRead, status_code=201)
def create_item(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    item = service.create(db, payload, tenant.id, current_user.id)
    item.added_by = current_user.id
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=SupplierRead)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, item_id, tenant.id)


@router.patch("/{item_id}", response_model=SupplierRead)
def update_item(
    item_id: str,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, item_id, payload, tenant.id)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, item_id, tenant.id)


# --- Vendor Documents (certs, agreements, qualification docs, etc.) ---

@router.get("/{item_id}/documents", response_model=list[SupplierDocumentRead])
def list_supplier_documents(
    item_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """List all documents for a supplier."""
    service.get(db, item_id, tenant.id)
    return db.query(SupplierDocument).filter(
        SupplierDocument.supplier_id == item_id
    ).order_by(SupplierDocument.created_at).all()


@router.post("/{item_id}/documents", response_model=SupplierDocumentRead, status_code=201)
async def upload_supplier_document(
    item_id: str,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a vendor document (cert, agreement, qualification record, etc.)."""
    service.get(db, item_id, tenant.id)

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

    # Save to uploads/{tenant_id}/suppliers/{item_id}/documents/
    upload_dir = os.path.join(settings.UPLOAD_DIR, tenant.id, "suppliers", item_id, "documents")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{_uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    doc = SupplierDocument(
        id=generate_uuid(),
        supplier_id=item_id,
        filename=file.filename,
        file_path=file_path,
        description=description or None,
        file_size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{item_id}/documents/{doc_id}/download")
def download_supplier_document(
    item_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Download a supplier document."""
    service.get(db, item_id, tenant.id)

    doc = db.query(SupplierDocument).filter(
        SupplierDocument.id == doc_id,
        SupplierDocument.supplier_id == item_id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not os.path.isfile(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{item_id}/documents/{doc_id}", status_code=204)
def delete_supplier_document(
    item_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Delete a supplier document and its file from disk."""
    service.get(db, item_id, tenant.id)

    doc = db.query(SupplierDocument).filter(
        SupplierDocument.id == doc_id,
        SupplierDocument.supplier_id == item_id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if os.path.isfile(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()
