"""Training endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_trainings(db: Session = Depends(get_db)):
    """List all trainings."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_trainings(db: Session = Depends(get_db)):
    """Create a new training."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_trainings(item_id: str, db: Session = Depends(get_db)):
    """Get a single training by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_trainings(item_id: str, db: Session = Depends(get_db)):
    """Update a training."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_trainings(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a training."""
    # TODO: implement
    return {"message": "not implemented"}
