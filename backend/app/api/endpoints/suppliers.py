"""Supplier endpoints — CRUD."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Supplier, number_prefix=None)


@router.get("/", response_model=list[SupplierRead])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=SupplierRead, status_code=201)
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
