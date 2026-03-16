"""Change Control endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_change_controls(db: Session = Depends(get_db)):
    """List all change control records."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_change_controls(db: Session = Depends(get_db)):
    """Create a new change control."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_change_controls(item_id: str, db: Session = Depends(get_db)):
    """Get a single change control by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_change_controls(item_id: str, db: Session = Depends(get_db)):
    """Update a change control."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_change_controls(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a change control."""
    # TODO: implement
    return {"message": "not implemented"}
