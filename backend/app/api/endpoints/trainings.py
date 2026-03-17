"""Training endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_current_tenant
from app.database import get_db
from app.models.training import Training, TrainingAssignment
from app.models.mixins import generate_uuid
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.training import (
    TrainingCreate, TrainingUpdate, TrainingRead,
    TrainingAssignmentCreate, TrainingAssignmentUpdate, TrainingAssignmentRead,
)
from app.services.base import CRUDService

router = APIRouter()
service = CRUDService(Training)


@router.get("/", response_model=list[TrainingRead])
def list_trainings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return service.list(db, tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=TrainingRead, status_code=201)
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
