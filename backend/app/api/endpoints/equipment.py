"""Equipment endpoints."""
import os
import uuid as _uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.core.config import settings
from app.database import get_db
from app.models.equipment import Equipment, EquipmentPhoto
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentRead, EquipmentPhotoRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Equipment, number_prefix="EQ")

PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tiff"}
MAX_PHOTO_SIZE = 20 * 1024 * 1024  # 20 MB


@router.get("", response_model=list[EquipmentRead])
def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("", response_model=EquipmentRead, status_code=201)
def create_equipment(
    payload: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    item = service.create(db, payload, tenant.id, current_user.id)
    item.added_by = current_user.id
    db.commit()
    db.refresh(item)
    return item


@router.get("/{equip_id}", response_model=EquipmentRead)
def get_equipment(
    equip_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, equip_id, tenant.id)


@router.patch("/{equip_id}", response_model=EquipmentRead)
def update_equipment(
    equip_id: str,
    payload: EquipmentUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, equip_id, payload, tenant.id)


@router.delete("/{equip_id}", status_code=204)
def delete_equipment(
    equip_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, equip_id, tenant.id)


# --- Equipment Photos ---

@router.get("/{equip_id}/photos", response_model=list[EquipmentPhotoRead])
def list_photos(
    equip_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """List all photos for a piece of equipment."""
    service.get(db, equip_id, tenant.id)
    return db.query(EquipmentPhoto).filter(
        EquipmentPhoto.equipment_id == equip_id
    ).order_by(EquipmentPhoto.created_at).all()


@router.post("/{equip_id}/photos", response_model=EquipmentPhotoRead, status_code=201)
async def upload_photo(
    equip_id: str,
    file: UploadFile = File(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Upload a photo for a piece of equipment."""
    service.get(db, equip_id, tenant.id)

    # Validate extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Only image files are accepted.",
        )

    contents = await file.read()
    if len(contents) > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {MAX_PHOTO_SIZE // (1024*1024)} MB.",
        )

    # Save to uploads/{tenant_id}/equipment/{equip_id}/photos/
    upload_dir = os.path.join(settings.UPLOAD_DIR, tenant.id, "equipment", equip_id, "photos")
    os.makedirs(upload_dir, exist_ok=True)

    safe_filename = f"{_uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    photo = EquipmentPhoto(
        id=generate_uuid(),
        equipment_id=equip_id,
        filename=file.filename,
        file_path=file_path,
        description=description or None,
        file_size=len(contents),
        uploaded_by=current_user.id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/{equip_id}/photos/{photo_id}/download")
def download_photo(
    equip_id: str,
    photo_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Download an equipment photo."""
    service.get(db, equip_id, tenant.id)

    photo = db.query(EquipmentPhoto).filter(
        EquipmentPhoto.id == photo_id,
        EquipmentPhoto.equipment_id == equip_id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if not os.path.isfile(photo.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=photo.file_path,
        filename=photo.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{equip_id}/photos/{photo_id}", status_code=204)
def delete_photo(
    equip_id: str,
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    """Delete an equipment photo and its file from disk."""
    service.get(db, equip_id, tenant.id)

    photo = db.query(EquipmentPhoto).filter(
        EquipmentPhoto.id == photo_id,
        EquipmentPhoto.equipment_id == equip_id,
    ).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if os.path.isfile(photo.file_path):
        os.remove(photo.file_path)

    db.delete(photo)
    db.commit()
