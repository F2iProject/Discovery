"""Equipment endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.equipment import Equipment
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Equipment, number_prefix="EQ")


@router.get("/", response_model=list[EquipmentRead])
def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=EquipmentRead, status_code=201)
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
