"""Calibration endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_calibrations(db: Session = Depends(get_db)):
    """List all calibration records."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_calibrations(db: Session = Depends(get_db)):
    """Create a new calibration."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_calibrations(item_id: str, db: Session = Depends(get_db)):
    """Get a single calibration by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_calibrations(item_id: str, db: Session = Depends(get_db)):
    """Update a calibration."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_calibrations(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a calibration."""
    # TODO: implement
    return {"message": "not implemented"}
