"""CAPA endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.capa import CAPA, CAPAAction
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.capa import (
    CAPACreate, CAPAUpdate, CAPARead,
    CAPAActionCreate, CAPAActionUpdate, CAPAActionRead,
)
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(CAPA, number_prefix="CAPA")


@router.get("", response_model=list[CAPARead])
def list_capas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("", response_model=CAPARead, status_code=201)
def create_capa(
    payload: CAPACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.create(db, payload, tenant.id, current_user.id)


@router.get("/{capa_id}", response_model=CAPARead)
def get_capa(
    capa_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, capa_id, tenant.id)


@router.patch("/{capa_id}", response_model=CAPARead)
def update_capa(
    capa_id: str,
    payload: CAPAUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.update(db, capa_id, payload, tenant.id)


@router.delete("/{capa_id}", status_code=204)
def delete_capa(
    capa_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, capa_id, tenant.id)


# --- CAPA Actions ---

@router.get("/{capa_id}/actions", response_model=list[CAPAActionRead])
def list_actions(
    capa_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, capa_id, tenant.id)
    return db.query(CAPAAction).filter(CAPAAction.capa_id == capa_id).all()


@router.post("/{capa_id}/actions", response_model=CAPAActionRead, status_code=201)
def create_action(
    capa_id: str,
    payload: CAPAActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, capa_id, tenant.id)
    action = CAPAAction(
        id=generate_uuid(),
        capa_id=capa_id,
        description=payload.description,
        action_type=payload.action_type,
        status=payload.status,
        assigned_to=payload.assigned_to,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.patch("/{capa_id}/actions/{action_id}", response_model=CAPAActionRead)
def update_action(
    capa_id: str,
    action_id: str,
    payload: CAPAActionUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.get(db, capa_id, tenant.id)
    action = db.query(CAPAAction).filter(
        CAPAAction.id == action_id,
        CAPAAction.capa_id == capa_id,
    ).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    update_data = payload.model_dump(exclude_unset=True)
    # Auto-set completed_at when status changes to completed
    if update_data.get("status") == "completed" and action.status != "completed":
        action.completed_at = datetime.now(timezone.utc)
    for field, value in update_data.items():
        setattr(action, field, value)
    db.commit()
    db.refresh(action)
    return action
