"""Risk endpoints — CRUD."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskUpdate, RiskRead
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Risk, number_prefix="RISK")


def _compute_risk_level(item, db: Session):
    """Compute risk_level from severity x likelihood."""
    if item.severity and item.likelihood:
        score = item.severity * item.likelihood
        if score <= 4:
            item.risk_level = "low"
        elif score <= 9:
            item.risk_level = "medium"
        elif score <= 16:
            item.risk_level = "high"
        else:
            item.risk_level = "critical"
        db.commit()
        db.refresh(item)


@router.get("/", response_model=list[RiskRead])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=RiskRead, status_code=201)
def create_item(
    payload: RiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    item = service.create(db, payload, tenant.id, current_user.id)
    _compute_risk_level(item, db)
    return item


@router.get("/{item_id}", response_model=RiskRead)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.get(db, item_id, tenant.id)


@router.patch("/{item_id}", response_model=RiskRead)
def update_item(
    item_id: str,
    payload: RiskUpdate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    item = service.update(db, item_id, payload, tenant.id)
    _compute_risk_level(item, db)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    service.delete(db, item_id, tenant.id)
