"""Supplier endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_suppliers(db: Session = Depends(get_db)):
    """List all suppliers."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_suppliers(db: Session = Depends(get_db)):
    """Create a new supplier."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_suppliers(item_id: str, db: Session = Depends(get_db)):
    """Get a single supplier by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_suppliers(item_id: str, db: Session = Depends(get_db)):
    """Update a supplier."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_suppliers(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a supplier."""
    # TODO: implement
    return {"message": "not implemented"}
