"""Training endpoints."""
import os
import uuid as _uuid

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.core.config import settings
from app.database import get_db
from app.models.training import Training, TrainingAssignment, TrainingMaterial
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.training import (
    TrainingCreate, TrainingUpdate, TrainingRead,
    TrainingAssignmentCreate, TrainingAssignmentUpdate, TrainingAssignmentRead,
    TrainingMaterialRead,
)
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Training)

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".rtf", ".odt", ".ods", ".odp",
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".mp4", ".webm", ".mov", ".avi",
    ".zip", ".tar", ".gz",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.get("", response_model=list[TrainingRead])
def list_trainings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("", response_model=TrainingRead, status_code=201)
def create_training(
    payload: TrainingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.create(db, payload, tenant.id, current_user.id)


@router.get("/{training_id}", response_model=TrainingRead)
def get_training(
    training_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, training_id, tenant.id)


@router.patch("/{training_id}", response_model=TrainingRead)
def update_training(
    training_id: str,
    payload: TrainingUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, training_id, payload, tenant.id)


@router.delete("/{training_id}", status_code=204)
def delete_training(
    training_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, training_id, tenant.id)


# --- Training Assignments ---

@router.get("/{training_id}/assignments", response_model=list[TrainingAssignmentRead])
def list_assignments(
    training_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    return db.query(TrainingAssignment).filter(
        TrainingAssignment.training_id == training_id
    ).all()


@router.post("/{training_id}/assignments", response_model=TrainingAssignmentRead, status_code=201)
def create_assignment(
    training_id: str,
    payload: TrainingAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    assignment = TrainingAssignment(
        id=generate_uuid(),
        training_id=training_id,
        user_id=payload.user_id,
        status=payload.status,
        due_date=payload.due_date,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.patch("/{training_id}/assignments/{assignment_id}", response_model=TrainingAssignmentRead)
def update_assignment(
    training_id: str,
    assignment_id: str,
    payload: TrainingAssignmentUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    assignment = db.query(TrainingAssignment).filter(
        TrainingAssignment.id == assignment_id,
        TrainingAssignment.training_id == training_id,
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    update_data = payload.model_dump(exclude_unset=True)
    # Auto-set completed_at when status changes to completed
    if update_data.get("status") == "completed" and assignment.status != "completed":
        assignment.completed_at = datetime.now(timezone.utc)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    db.commit()
    db.refresh(assignment)
    return assignment


# --- Training Materials (slides, handouts, videos, etc.) ---

@router.get("/{training_id}/materials", response_model=list[TrainingMaterialRead])
def list_materials(
    training_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    return db.query(TrainingMaterial).filter(
        TrainingMaterial.training_id == training_id
    ).order_by(TrainingMaterial.created_at).all()


@router.post("/{training_id}/materials", response_model=TrainingMaterialRead, status_code=201)
async def upload_material(
    training_id: str,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
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
    upload_dir = os.path.join(settings.UPLOAD_DIR, tenant.id, "trainings", training_id, "materials")
    os.makedirs(upload_dir, exist_ok=True)
    safe_filename = f"{_uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    material = TrainingMaterial(
        id=generate_uuid(),
        training_id=training_id,
        filename=file.filename,
        file_path=file_path,
        description=description or None,
        file_size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.get("/{training_id}/materials/{material_id}/download")
def download_material(
    training_id: str,
    material_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    material = db.query(TrainingMaterial).filter(
        TrainingMaterial.id == material_id,
        TrainingMaterial.training_id == training_id,
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not os.path.isfile(material.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        path=material.file_path,
        filename=material.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{training_id}/materials/{material_id}", status_code=204)
def delete_material(
    training_id: str,
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, training_id, tenant.id)
    material = db.query(TrainingMaterial).filter(
        TrainingMaterial.id == material_id,
        TrainingMaterial.training_id == training_id,
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if os.path.isfile(material.file_path):
        os.remove(material.file_path)
    db.delete(material)
    db.commit()
