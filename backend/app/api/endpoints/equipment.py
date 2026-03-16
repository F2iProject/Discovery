"""Equipment endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_equipment(db: Session = Depends(get_db)):
    """List all equipment records."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_equipment(db: Session = Depends(get_db)):
    """Create a new equipment."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_equipment(item_id: str, db: Session = Depends(get_db)):
    """Get a single equipment by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_equipment(item_id: str, db: Session = Depends(get_db)):
    """Update a equipment."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_equipment(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a equipment."""
    # TODO: implement
    return {"message": "not implemented"}
