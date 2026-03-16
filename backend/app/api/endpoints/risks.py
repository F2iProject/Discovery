"""Risk endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_risks(db: Session = Depends(get_db)):
    """List all risks."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_risks(db: Session = Depends(get_db)):
    """Create a new risk."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_risks(item_id: str, db: Session = Depends(get_db)):
    """Get a single risk by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_risks(item_id: str, db: Session = Depends(get_db)):
    """Update a risk."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_risks(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a risk."""
    # TODO: implement
    return {"message": "not implemented"}
