"""Calibration endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.calibration import CalibrationRecord
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.calibration import CalibrationCreate, CalibrationUpdate, CalibrationRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(CalibrationRecord)


@router.get("/", response_model=list[CalibrationRead])
def list_calibrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=CalibrationRead, status_code=201)
def create_calibration(
    payload: CalibrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    item = service.create(db, payload, tenant.id, current_user.id)
    item.performed_by = current_user.id
    db.commit()
    db.refresh(item)
    return item


@router.get("/{record_id}", response_model=CalibrationRead)
def get_calibration(
    record_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, record_id, tenant.id)


@router.patch("/{record_id}", response_model=CalibrationRead)
def update_calibration(
    record_id: str,
    payload: CalibrationUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, record_id, payload, tenant.id)


@router.delete("/{record_id}", status_code=204)
def delete_calibration(
    record_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, record_id, tenant.id)
