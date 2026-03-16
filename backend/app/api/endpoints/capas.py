"""CAPA endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_capas(db: Session = Depends(get_db)):
    """List all CAPAs."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_capas(db: Session = Depends(get_db)):
    """Create a new capa."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_capas(item_id: str, db: Session = Depends(get_db)):
    """Get a single capa by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_capas(item_id: str, db: Session = Depends(get_db)):
    """Update a capa."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_capas(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a capa."""
    # TODO: implement
    return {"message": "not implemented"}
