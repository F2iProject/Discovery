"""Document endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.document import Document, DocumentVersion
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentRead,
    DocumentVersionCreate, DocumentVersionRead,
)
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Document, number_prefix="DOC")


@router.get("/", response_model=list[DocumentRead])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=DocumentRead, status_code=201)
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
